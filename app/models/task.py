# -*- encoding: utf-8 -*-
from logging import getLogger

from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import PROTECT, CharField, FloatField, TextField, IntegerField, BooleanField, Q, CheckConstraint, UniqueConstraint
from django.utils.html import format_html

from django.urls import reverse
from simple_history.models import HistoricForeignKey
from model_utils.managers import InheritanceManager

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
    load_calc = IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        blank=False, null=False,
        verbose_name="Calculated Load",
    )
    load_calc_first = IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        blank=False, null=False,
        verbose_name="Calculated Load (first time)",
    )

    # === CHANGEABLE FIELDS ===
    name = CharField(max_length=128, blank=False)

    is_required = BooleanField(
        default=False,
        verbose_name="Is required",
        help_text=format_html("Does this task <i>have</i> to be assigned?"),
    )
    is_unique = BooleanField(
        default=False,
        verbose_name="Is unique",
        help_text=format_html("Can multiple staff perform this task, or only one?"),
    )

    academic_group = HistoricForeignKey(
        AcademicGroup, on_delete=PROTECT, null=True, blank=True,
        related_name='task_set',
    )

    load_fixed = IntegerField(
        default=0,
        validators=[
            MinValueValidator(0)
        ],
        verbose_name="Fixed load hours",
    )
    load_fixed_first = IntegerField(
        default=0,
        validators=[
            MinValueValidator(0)
        ],
        blank=True, null=True,
        verbose_name="First-time load adjustment",
        help_text="Load for first-time staff is fixed load plus first-time adjustment."
    )
    load_multiplier = FloatField(
        default=1.0,
        validators=[
            MinValueValidator(0.1),
            MaxValueValidator(10.00)
        ],
        blank=False,
        verbose_name="Final load multiplier",
        help_text="Multiplier applied to final load calculation."
    )

    # ==========================================================================
    # *Not* used by TaskUnitLead.
    # ==========================================================================
    load_function = HistoricForeignKey(
        LoadFunction,
        blank=True, null=True,
        on_delete=PROTECT,
        help_text="Function by which student load for this task scales",
    )
    students = IntegerField(
        null=True, blank=True,
        help_text="Number of students for load function and/or co-ordinator equations. If this task belongs to a Unit, falls back to Unit students if empty.",
    )
    # ==========================================================================

    # ==========================================================================
    # TaskUnitLead components. Polymorphism and SimpleHistory don't play nice.
    # ==========================================================================
    unit = HistoricForeignKey(
        Unit, on_delete=PROTECT, null=True, blank=True,
        related_name='task_set',
    )
    is_lead = BooleanField(
        default=False,
        verbose_name="Is Unit Lead",
        help_text="If set, adds load as calculated using the equations for unit leads.",
    )
    coursework_fraction = FloatField(
        default=0.0,
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(1.0)
        ],
        verbose_name="Fraction of coursework marked",
    )
    exam_fraction = FloatField(
        default=0.0,
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(1.0)
        ],
        verbose_name="Fraction of exams marked",
    )
    # ==========================================================================

    description = TextField(blank=False)
    notes = TextField(blank=True)

    class Meta:
        ordering = ('unit', 'name',)
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
        constraints = [
            UniqueConstraint(
                fields=['unit', 'name'],
                name='unit_task_name',
                violation_error_message="Units cannot have multiple tasks with the same name."
            ),
            UniqueConstraint(
                fields=['academic_group', 'name'],
                name='unit_group_name',
                violation_error_message="Academic groups cannot have multiple tasks with the same name."
            ),
            CheckConstraint(
                check=(Q(unit__isnull=False) & Q(is_lead=True)) | Q(is_lead=False),
                name='unit_lead_required',
                violation_error_message="Cannot be co-ordinator of a Unit without a linked unit.",
            ),
        ]

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

    def get_instance_header(self, text: str|None = None) -> str:
        """
        Overrides the default instance header to include the unit, with link, if present.
        :param text: Override text.
        :return: The rendered HTML template for this model.
        """
        return super().get_instance_header(text=self.get_name())

    def get_absolute_url(self) -> str:
        """
        Preprend the unit if this is a unit task
        """
        if self.unit:
            return f"/{Unit.url_root}/{self.unit.pk}/{self.pk}/"
        elif self.academic_group:
            return f"/{AcademicGroup.url_root}/{self.academic_group.pk}/{self.pk}/"
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
        logger.debug(f"{self}: Updating load...")

        students: int = self.students
        if not self.students and self.unit:
            students = self.unit.students

        load_calc = self.calculate_load(
            students=students,
            is_first_time=False,
        )
        load_calc_first = self.calculate_load(
            students=students,
            is_first_time=True,
        )

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

    def calculate_load(
            self,
            students: int|None,
            is_first_time: bool = False
    ) -> float:
        """

        :return:
        """
        if self.is_lead:
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

            load_calc_first = load + self.load_fixed + load_lecture_first + self.load_fixed_first
            load_calc = load + self.load_fixed + load_lecture

        else:
            # ==== IF THIS IS NOT A UNIT CO-ORDINATOR ====
            # Much simpler logic
            load_calc = self.load_fixed

            if self.load_function:
                try:
                    load_calc += self.load_function.evaluate(students, self.unit)
                except Exception as calculation_exception:
                    raise calculation_exception

            load_calc_first = load_calc + self.load_fixed_first

        if is_first_time:
            return load_calc_first * self.load_multiplier
        else:
            return load_calc * self.load_multiplier

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
