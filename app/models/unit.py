# -*- encoding: utf-8 -*-
from typing import Optional, Union, List
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Model, CharField, BooleanField, TextField, ForeignKey, Index, IntegerField, FloatField, CheckConstraint, Q, F
from django.db.models.deletion import PROTECT
from django.db.models.manager import Manager
from django.urls import reverse_lazy
from django.template.loader import render_to_string
from model_utils.managers import QueryManager

from app.models.academic_group import AcademicGroup
from app.models.standard_load import StandardLoad, get_current_standard_load


class Unit(Model):
    """

    """
    icon = 'book'
    url_root = 'unit'

    code = CharField(max_length=16, blank=False, unique=True)
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

    credit_hours = IntegerField(
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
        indexes = [
            Index(fields=['code']),
        ]
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

    def get_absolute_url(self) -> str:
        """
        :return: The URL for the detail view of this particular instance of the model
        """
        return reverse_lazy('unit_detail', args=[self.code])

    def get_marked_dissertation_count(self) -> int|None:
        """
        :return: Returns the total number of unit dissertations marked
        """
        if self.has_dissertation:
            return sum(
                self.task_set.values_list('student', flat=True)
            )

    def get_instance_header(self) -> str:
        """
        The header for a page referring to a specific instance of this model
        :return: The rendered HTML template for this model.
        """
        return render_to_string(
            template_name='app/title.html',
            context={
                'icon': self.icon, 'url': self.get_absolute_url(),
                'text': self
            }
        )

    @staticmethod
    def get_model_url() -> str:
        """
        :return: The URL for the view listing all of this model
        """
        return reverse_lazy(Unit.url_root+'_list')

    @staticmethod
    def get_model_header() -> str:
        """
        The header for a page listing all of this model
        :return: The HTML template for this model.
        """
        return render_to_string(
            template_name='app/title.html',
            context={
                'icon': Unit.icon, 'url': Unit.get_model_url(),
                'text': Unit._meta.verbose_name_plural.title()
            }
        )
