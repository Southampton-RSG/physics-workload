# -*- encoding: utf-8 -*-
from logging import getLogger, DEBUG
from typing import Type

from django.contrib.auth.models import AbstractUser
from django.template.loader import render_to_string
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Model, ForeignKey, PROTECT, CharField, FloatField, TextField, IntegerField, BooleanField, Manager
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from model_utils.managers import QueryManager
from simple_history.models import HistoricalRecords

from app.models.standard_load import StandardLoad, get_current_standard_load
from app.models.load_function import LoadFunction
from app.models.unit import Unit
from app.models.mixins import ModelCommonMixin

# Set up logging for this file
logger = getLogger(__name__)


class Task(ModelCommonMixin, Model):
    """
    This is the model for tasks
    """
    icon = "clipboard"
    url_root = "task"

    # === CACHED LOADS ===
    load_calc = FloatField(
        default=0.0, validators=[MinValueValidator(0.0)], blank=False, null=False,
        verbose_name="Calculated Load"
    )
    load_calc_first = FloatField(
        default=0.0, validators=[MinValueValidator(0.0)], blank=False, null=False,
        verbose_name="Calculated Load (first time)"
    )

    name = CharField(max_length=128, blank=False)

    is_active = BooleanField(default=True)
    objects_active = QueryManager(is_active=True)
    objects = Manager()

    history = HistoricalRecords()

    number_needed = IntegerField(
        null=False, blank=False, default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Required",
    )

    unit = ForeignKey(
        Unit, on_delete=PROTECT, null=True, blank=True,
        related_name='task_set',
    )

    load_fixed = FloatField(
        default=0.0, validators=[MinValueValidator(0.0)],
        verbose_name="Fixed load hours",
    )
    load_fixed_first = FloatField(
        default=0.0, validators=[MinValueValidator(0.0)], blank=True, null=True,
        verbose_name="Extra load hours for first-time",
    )

    load_function = ForeignKey(
        LoadFunction, blank=True, null=True, on_delete=PROTECT,
        help_text="Function by which student load for this task scales",
    )
    students = IntegerField(
        null=True, blank=True,
        help_text="Number of students for scaling load, if not the whole unit",
    )

    coursework_fraction = FloatField(
        default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="Fraction of coursework marked",
    )
    exam_fraction = FloatField(
        default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="Fraction of exams marked",
    )

    description = TextField(blank=False)
    notes = TextField(blank=True)

    class Meta:
        ordering = ('is_active', 'unit', 'name',)
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'

    def __str__(self):
        """
        :return: The name, with unit if it's a unit, with first-time load if valid
        """
        text = f"{self.name}"
        if self.unit:
            text = f"{self.unit.code} - "+text

        if self.load_calc != self.load_calc_first:
            text += f" [{self.load_calc:.0f} / {self.load_calc_first:.0f}]"
        else:
            text += f" [{self.load_calc:.0f}]"

        return text

    def get_name(self):
        return f"{self.unit.code} - {self.name}"

    def get_instance_header(self) -> str:
        """
        Overrides the default instance header to include the unit, with link, if present.
        :return: The rendered HTML template for this model.
        """
        if self.unit:
            return render_to_string(
                template_name='app/header/header_unit.html',
                context={
                    'icon': self.icon, 'url': self.get_absolute_url(),
                    'text': self.name,
                    'unit_text': self.unit.code, 'unit_url': self.unit.get_absolute_url(),
                }
            )
        else:
            return render_to_string(
                template_name='app/header/header.html',
                context={
                    'icon': self.icon, 'url': self.get_absolute_url(),
                    'text': self
                }
            )

    def has_any_provisional(self) -> bool:
        return any(self.assignment_set.values_list('is_provisional', flat=True))

    def has_any_first_time(self) -> bool:
        return any(self.assignment_set.values_list('is_first_time', flat=True))

    def has_access(self, user: AbstractUser) -> bool:
        """
        Only users assigned to a task can see the details
        :param user: The user
        :return: True if the user is assigned to this task
        """
        return user.staff in self.assignment_set.values_list('staff', flat=True)


@receiver(pre_save, sender=Task)
def calculate_load_for_task(
        sender: Type[Task], instance: Task, **kwargs
):
    """
    Called when the model is being saved, updates the calculated load
    """
    load: float = 0
    logger.debug(f"{instance}: Updating load...")

    if instance.unit and (instance.coursework_fraction or instance.exam_fraction):
        # ==== IF THIS IS A UNIT CO-ORDINATOR ====
        # SPREADSHEET LOGIC
        standard_load: StandardLoad = get_current_standard_load()
        unit: Unit = instance.unit

        # ($I2+$Q2) = "Number of Lectures/Problem Classes Run by Coordinator" + "Number of Synoptic Lectures"
        contact_sessions: int = unit.lectures + unit.synoptic_lectures + unit.problem_classes

        # (($I2+$Q2)*3.5) or (($I2+$Q2)*6)
        load_lecture: float = contact_sessions * standard_load.load_lecture
        load_lecture_first: float = contact_sessions * standard_load.load_lecture_first

        load_coursework: float = 0
        if unit.coursework and instance.coursework_fraction:
            # ($J2*2) = "Coursework (number of items prepared)"
            load_coursework += unit.coursework * standard_load.load_coursework_set

            # ($L2*$O2*2) = "Coursework (fraction of unit mark)" * "Total Number of CATS"
            load_coursework += unit.coursework_mark_fraction * unit.credits * standard_load.load_coursework_credit

            # ($J2+$L2*$Q2) = "Coursework (number of items prepared)" + "Coursework (fraction of unit mark)" * "Total Number of CATS"
            # (0.1667 * [] * $K2 * $P2) = "Fraction of Coursework marked by coordinator" * "Number of Students"
            load_coursework += (unit.coursework + unit.coursework_mark_fraction * unit.credits) * \
                                            instance.coursework_fraction * unit.students * standard_load.load_coursework_marked

        load_exam: float = 0
        if instance.exam_fraction:
            # ($M2*O2*2) = "Examination (fraction of unit mark)" * "Total Number of CATS"
            load_exam += unit.exam_mark_fraction * unit.credits * standard_load.load_exam_credit

            # ($P2*$N2*1) = "Number of Students" * "Fraction of Exams Marked by Coordinator"
            load_exam += unit.students * instance.exam_fraction * standard_load.load_exam_marked

        load: float = load_coursework + load_exam

        if instance.load_function:
            load += instance.load_function.evaluate(instance.students)
        elif instance.students:
            raise Exception("Task has students but no load function")

        instance.load_calc_first = load + instance.load_fixed + load_lecture_first + instance.load_fixed_first
        instance.load_calc = load + instance.load_fixed + load_lecture

    else:
        # ==== IF THIS IS NOT A UNIT CO-ORDINATOR ====
        # Much simpler logic
        if instance.load_function:
            try:
                load += instance.load_function.evaluate(instance.students)
            except Exception as calculation_exception:
                raise calculation_exception

        instance.load_calc = instance.load_fixed + load
        instance.load_calc_first = instance.load_calc + instance.load_fixed_first


@receiver(post_save, sender=Task)
def apply_updated_load(
        sender: Type[Task], instance: Task, **kwargs
):
    """
    Called after a task is updated - updates the load on all linked staff.
    """
    logger.debug(f"{instance}: Updated load, updating related models")

    for assignment in instance.assignment_set.all():
        # This could be done as an Update query with aggregation
        logger.debug(f"{instance}: Updating balance on assigned staff {assignment.staff}")
        assignment.staff.calculate_load_balance()
