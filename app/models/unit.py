# -*- encoding: utf-8 -*-
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Model, CharField, BooleanField, TextField, ForeignKey, IntegerField, FloatField, CheckConstraint, Q, F
from django.db.models.deletion import PROTECT
from django.db.models.manager import Manager
from model_utils.managers import QueryManager

from app.models.academic_group import AcademicGroup
from app.models.mixins import ModelCommonMixin


class Unit(ModelCommonMixin, Model):
    """
    Academic unit, e.g. PHYS!001
    """
    icon = 'book'
    url_root = 'unit'

    code = CharField(max_length=16, blank=False, unique=True, primary_key=True)
    name = CharField(max_length=128, blank=False, unique=True)
    academic_group = ForeignKey(
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

    is_active = BooleanField(default=True)
    objects_active = QueryManager(is_active=True)
    objects = Manager()

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
                self.task_set.values_list('student', flat=True)
            )

    def has_access(self, user: AbstractUser) -> bool:
        """
        Only users assigned to a unit can see the details
        :param user: The user
        :return: True if the user is assigned to a task in this unit
        """
        for task in self.task_set.all():
            if user.staff in task.assignment_set.values_list('staff', flat=True):
                return True

        return False
