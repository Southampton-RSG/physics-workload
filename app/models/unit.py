# -*- encoding: utf-8 -*-
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import BooleanField, CharField, CheckConstraint, F, FloatField, IntegerField, Q, TextField
from django.db.models.deletion import PROTECT
from simple_history.models import HistoricForeignKey

from app.models.academic_group import AcademicGroup
from app.models.common import ModelCommon


class Unit(ModelCommon):
    """
    Academic unit, e.g. PHYS1001
    """
    icon = 'book'
    url_root = 'module'

    code = CharField(max_length=16, blank=False, unique=True, primary_key=True)
    name = CharField(max_length=128, blank=False, unique=True)
    academic_group = HistoricForeignKey(
        AcademicGroup, blank=True, null=True, on_delete=PROTECT,
        verbose_name='Group',
    )

    students = IntegerField(
        null=True, blank=True, default=None, validators=[MinValueValidator(0)],
    )

    lectures = IntegerField(
        default=0, verbose_name="Lectures", validators=[MinValueValidator(0)],
    )
    problem_classes = IntegerField(
        default=0, verbose_name="Problem Classes", validators=[MinValueValidator(0)],
    )
    coursework = IntegerField(
        default=0, verbose_name="Coursework Prepared", validators=[MinValueValidator(0)],
    )
    synoptic_lectures = IntegerField(
        default=0, verbose_name="Synoptic Lectures", validators=[MinValueValidator(0)],
    )
    exams = IntegerField(
        default=0, verbose_name="Exams", validators=[MinValueValidator(0)],
    )

    credits = IntegerField(
        null=True, blank=True, verbose_name="CATS", validators=[MinValueValidator(0)],
    )
    exam_mark_fraction = FloatField(
        null=True, blank=True, verbose_name="Exam mark fraction",
        validators=[MinValueValidator(0), MaxValueValidator(1)],
    )
    coursework_mark_fraction = FloatField(
        null=True, blank=True, verbose_name="Coursework mark fraction",
        validators=[MinValueValidator(0), MaxValueValidator(1)],
    )
    has_dissertation = BooleanField(default=False)
    has_placement = BooleanField(default=False)

    description = TextField(blank=True)
    notes = TextField(blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Module'
        verbose_name_plural = 'Modules'
        constraints = [
            CheckConstraint(
                check=Q(exam_mark_fraction__lte=1-F('coursework_mark_fraction')) | \
                      (Q(exam_mark_fraction__isnull=True) & Q(coursework_mark_fraction__isnull=True)),
                name='total_mark_fraction',
                violation_error_message="Total mark fraction must be less than 1, or both mark fractions must be empty.",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"

    def get_short_name(self) -> str:
        """
        :return: Just returns the code. Needed for parity with the AcademicGroup model, for Task ownership.
        """
        return f"{self.code}"

    def get_instance_header_short(self) -> str:
        """
        :return: Wraps instance header, but only uses a short nane,
        """
        return super().get_instance_header(text=self.code)

    def get_marked_dissertation_count(self) -> int|None:
        """
        :return: Returns the total number of dissertations marked
        """
        if self.has_dissertation:
            return sum(
                self.task_set.values_list('student', flat=True)
            )

    def has_access(self, user: AbstractUser) -> bool:
        """
        Only users assigned to a module can see the details
        :param user: The user
        :return: True if the user is assigned to a task in this module
        """
        if super().has_access(user):
            return True
        elif not user.is_anonymous:
            for task in self.task_set.all():
                if user.staff in task.assignment_set.values_list('staff', flat=True):
                    return True

        return False

    def update_load(self) -> bool:
        """
        :return: True if the load of any of the tasks needed updating.
        """
        recalculate_loads: bool = False

        for task in self.task_set.all():
            # We don't use this but let's ignore the warning for now
            task_old_load_calc: int = task.load_calc  # noqa: F841
            task_old_load_calc_first: int = task.load_calc_first  # noqa: F841

            task_load_has_changed: bool = task.update_load()

            if task_load_has_changed:
                # If it actually has an effect, then flag that fact and update the task
                recalculate_loads = True

                for assignment in task.assignment_set.all():
                    if assignment.update_load():
                        # If this has actually changed the assignment loads too, then update them and the staff
                        assignment.staff.update_load_assigned()

        if recalculate_loads:
            # If we need to update the standard load, then do so
            from app.models.standard_load import StandardLoad
            standard_load: StandardLoad = StandardLoad.objects.latest()
            standard_load.update_target_load_per_fte()

        return recalculate_loads
