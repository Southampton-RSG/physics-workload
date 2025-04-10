# -*- encoding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Model, CharField, BooleanField, TextField, IntegerField, FloatField, CheckConstraint, Q, F
from django.db.models.deletion import PROTECT
from simple_history.models import HistoricForeignKey

from app.models.academic_group import AcademicGroup
from app.models.common import ModelCommon


class Unit(ModelCommon, Model):
    """
    Academic unit, e.g. PHYS!001
    """
    icon = 'book'
    url_root = 'unit'

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
        verbose_name = 'Unit'
        verbose_name_plural = 'Units'
        constraints = [
            CheckConstraint(
                check=Q(exam_mark_fraction__exact=1-F('coursework_mark_fraction')) | \
                      (Q(exam_mark_fraction__isnull=True) & Q(coursework_mark_fraction__isnull=True)),
                name='total_mark_fraction',
                violation_error_message="Total mark fraction must be 1, or both mark fractions must be empty.",
            )
        ]

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"

    def get_marked_dissertation_count(self) -> int|None:
        """
        :return: Returns the total number of unit dissertations marked
        """
        if self.has_dissertation:
            return sum(
                self.task_set.filter(is_removed=False).values_list('student', flat=True)
            )

    def has_access(self, user: AbstractUser) -> bool:
        """
        Only users assigned to a unit can see the details
        :param user: The user
        :return: True if the user is assigned to a task in this unit
        """
        if super().has_access(user):
            return True
        elif not user.is_anonymous:
            for task in self.task_set.all():
                if user.staff in task.assignment_set.filter(is_removed=False).values_list('staff', flat=True):
                    return True

        return False

    def update_load(self) -> bool:
        """

        :return:
        """
        recalculate_loads: bool = False

        for task in self.task_set.filter(is_removed=False).all():
            task_old_load_calc = task.load_calc
            task_old_load_calc_first = task.load_calc_first
            task_load_has_changed: bool = task.update_load()

            if task_load_has_changed:
                # If it actually has an effect, then flag that fact and update the task
                task.save()
                recalculate_loads = True

                for assignment in task.assignment_set.filter(is_removed=False).all():
                    if assignment.update_load():
                        # If this has actually changed the assignment loads too, then update them and the staff
                        assignment.staff.update_load_assigned()

        if recalculate_loads:
            # If we need to update the standard load, then do so
            from app.models.standard_load import StandardLoad
            standard_load: StandardLoad = StandardLoad.objects.latest()
            standard_load.update_target_load_per_fte()
