# -*- encoding: utf-8 -*-
from typing import Optional, Union, List
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Model, CharField, BooleanField, TextField, ForeignKey, Index, IntegerField, FloatField
from django.db.models.deletion import PROTECT
from django.db.models.manager import Manager
from django.urls import reverse_lazy
from model_utils.managers import QueryManager

from app.models.academic_group import AcademicGroup
from app.models.academic_year import AcademicYear, get_latest_academic_year


class Module(Model):
    """

    """
    code = CharField(max_length=16, blank=False, unique=True)
    name = CharField(max_length=128, blank=False, unique=True)
    academic_group = ForeignKey(
        AcademicGroup, blank=True, null=True, on_delete=PROTECT,
        verbose_name='Group', help_text="The group, if any, responsible for this module",
    )

    has_dissertation = BooleanField(default=False)
    has_placement = BooleanField(default=False)

    description = TextField(blank=True)

    module = ForeignKey(
        Module, blank=False, null=False, on_delete=PROTECT,
        related_name='module_years',
    )
    academic_year = ForeignKey(
        AcademicYear, blank=False, null=False, on_delete=PROTECT,
        default=get_latest_academic_year,
    )
    students = IntegerField(
        null=True, blank=True, default=None, validators=[MinValueValidator(0)],
    )
    credit_hours = IntegerField(
        null=True, blank=True, verbose_name="Credit Hours", validators=[MinValueValidator(0)],
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

    exam_mark_fraction = FloatField(
        null=True, blank=True, verbose_name="Exam fraction of total mark",
        validators=[MinValueValidator(0), MaxValueValidator(1)],
    )
    coursework_mark_fraction = FloatField(
        null=True, blank=True, verbose_name="Coursework fraction of total mark",
        validators=[MinValueValidator(0), MaxValueValidator(1)],
    )

    notes = TextField(blank=True)

    is_active = BooleanField(default=True)
    objects_active = QueryManager(is_active=True)
    objects = Manager()

    class Meta:
        indexes = [
            Index(fields=['code']),
        ]
        ordering = ['name']
        verbose_name = 'Module'
        verbose_name_plural = 'Modules'

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"

    def get_absolute_url(self) -> str:
        return reverse_lazy('module_detail', args=[self.code])

    def get_marked_dissertation_count(self) -> int|None:
        """
        :return: Returns the total number of module dissertations marked
        """
        if self.has_dissertation:
            return sum(
                self.taskmodule_set.values_list('student', flat=True)
            )