# -*- encoding: utf-8 -*-
from logging import getLogger
from typing import Type

from django.contrib.auth.models import AbstractUser
from django.template.loader import render_to_string
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Model, ForeignKey, PROTECT, CharField, FloatField, TextField, IntegerField

from django.urls import reverse
from simple_history.models import HistoricForeignKey

from app.models import AcademicGroup
from app.models.load_function import LoadFunction
from app.models.unit import Unit
from app.models.common import ModelCommon

# Set up logging for this file
logger = getLogger(__name__)


class Task(ModelCommon):
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

    number_needed = IntegerField(
        null=False, blank=False, default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Required",
    )

    unit = HistoricForeignKey(
        Unit, on_delete=PROTECT, null=True, blank=True,
        related_name='task_set',
    )
    academic_group = HistoricForeignKey(
        AcademicGroup, on_delete=PROTECT, null=True, blank=True,
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

    load_function = HistoricForeignKey(
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
        ordering = ('unit', 'name',)
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'

    def __str__(self):
        """
        :return: The name, with unit if it's a unit, with first-time load if valid
        """
        text = f"{self.name}"
        if self.unit:
            text = f"{self.unit.code} - " + text
        elif self.academic_group:
            text = f"{self.academic_group.short_name} - " + text

        if self.load_calc != self.load_calc_first:
            text += f" [{self.load_calc:.0f} / {self.load_calc_first:.0f}]"
        else:
            text += f" [{self.load_calc:.0f}]"

        return text

    def get_name(self):
        """
        :return: The name of the task, with unit code if possible
        """
        if self.unit:
            return f"{self.unit.code} - {self.name}"
        elif self.academic_group:
            return f"{self.academic_group.short_name} - {self.name}"
        else:
            return f"{self.name}"

    def get_instance_header(self, text: str|None = None, suffix: str|None = None) -> str:
        """
        Overrides the default instance header to include the unit, with link, if present.
        :param text: Override text.
        :param suffix: Optional suffix.
        :return: The rendered HTML template for this model.
        """
        return super().get_instance_header(text=self.get_name(), suffix=suffix)

    def get_absolute_url(self) -> str:
        """
        Preprend the unit if this is a unit task
        """
        if self.unit:
            return f"{Unit.url_root}/{self.unit.pk}/{self.pk}/"
        elif self.academic_group:
            return f"{AcademicGroup.url_root}/{self.academic_group.pk}/{self.pk}/"
        else:
            return super().get_absolute_url()

    def has_any_provisional(self) -> bool:
        return any(self.assignment_set.filter(is_removed=False).values_list('is_provisional', flat=True))

    def has_any_first_time(self) -> bool:
        return any(self.assignment_set.filter(is_removed=False).values_list('is_first_time', flat=True))

    def has_access(self, user: AbstractUser) -> bool:
        """
        Only users assigned to a task can see the details
        :param user: The user
        :return: True if the user is assigned to this task
        """
        if super().has_access(user):
            return True
        elif user.is_anonymous:
            return False
        else:
            return user.staff in self.assignment_set.filter(is_removed=False).values_list('staff', flat=True)

    def update_load(self) -> True:
        """
        Updates the load for this task. Does not save to DB; that needs to be done in the calling function.
        :return: True if the load has changed, false if not.
        """
        load: float = 0
        logger.debug(f"{self}: Updating load...")

        if self.unit and (self.coursework_fraction or self.exam_fraction):
            # ==== IF THIS IS A UNIT CO-ORDINATOR ====
            # SPREADSHEET LOGIC
            from app.models.standard_load import StandardLoad
            standard_load: StandardLoad = StandardLoad.available_objects.latest()

            unit: Unit = self.unit

            # ($I2+$Q2) = "Number of Lectures/Problem Classes Run by Coordinator" + "Number of Synoptic Lectures"
            contact_sessions: int = unit.lectures + unit.synoptic_lectures + unit.problem_classes

            # (($I2+$Q2)*3.5) or (($I2+$Q2)*6)
            load_lecture: float = contact_sessions * standard_load.load_lecture
            load_lecture_first: float = contact_sessions * standard_load.load_lecture_first

            load_coursework: float = 0
            if unit.coursework and self.coursework_fraction:
                # ($J2*2) = "Coursework (number of items prepared)"
                load_coursework += unit.coursework * standard_load.load_coursework_set

                # ($L2*$O2*2) = "Coursework (fraction of unit mark)" * "Total Number of CATS"
                load_coursework += unit.coursework_mark_fraction * unit.credits * standard_load.load_coursework_credit

                # ($J2+$L2*$Q2) = "Coursework (number of items prepared)" + "Coursework (fraction of unit mark)" * "Total Number of CATS"
                # (0.1667 * [] * $K2 * $P2) = "Fraction of Coursework marked by coordinator" * "Number of Students"
                load_coursework += (unit.coursework + unit.coursework_mark_fraction * unit.credits) * \
                                                self.coursework_fraction * unit.students * standard_load.load_coursework_marked

            load_exam: float = 0
            if self.exam_fraction:
                # ($M2*O2*2) = "Examination (fraction of unit mark)" * "Total Number of CATS"
                load_exam += unit.exam_mark_fraction * unit.credits * standard_load.load_exam_credit

                # ($P2*$N2*1) = "Number of Students" * "Fraction of Exams Marked by Coordinator"
                load_exam += unit.students * self.exam_fraction * standard_load.load_exam_marked

            load: float = load_coursework + load_exam

            if self.load_function:
                load += self.load_function.evaluate(self.students)
            elif self.students:
                raise Exception("Task has students but no load function")

            load_calc_first = load + self.load_fixed + load_lecture_first + self.load_fixed_first
            load_calc = load + self.load_fixed + load_lecture

        else:
            # ==== IF THIS IS NOT A UNIT CO-ORDINATOR ====
            # Much simpler logic
            if self.load_function:
                try:
                    load += self.load_function.evaluate(self.students)
                except Exception as calculation_exception:
                    raise calculation_exception

            load_calc = self.load_fixed + load
            load_calc_first = load_calc + self.load_fixed_first

        if self.load_calc != load_calc or self.load_calc_first != load_calc_first:
            # If this has changed any of the values, then update the assignments and return that it has
            self.load_calc_first = load_calc_first
            self.load_calc = load_calc
            self.save()

            for assignment in self.assignment_set.filter(is_removed=False).all():
                assignment.update_load()

            return True
        else:
            return False

#
# @receiver(post_delete, sender=Task)
# def update_related_models(sender: Type[Task], instance: Task, **kwargs):
#     """
#
#     :param sender:
#     :param instance: The deleted instance. It now only exists in memory!
#     :param kwargs:
#     :return:
#     """
#     from app.models.standard_load import StandardLoad
#     logger.info(
#         f"Deleted {type(instance)} {instance}; updating the standard load."
#     )
#     StandardLoad.objects.latest().update_calculated_loads()
