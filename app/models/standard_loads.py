# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.core.validators import MinValueValidator
from django.db.models import Model, FloatField, ForeignKey, PROTECT

from app.models.academic_year import AcademicYear, get_latest_academic_year



class StandardLoads(Model):
    """
    Standard load hours per task, for a given year
    """
    lecture = FloatField(
        blank=False, null=False,
        validators=[
            MinValueValidator(0.0),
        ],
        verbose_name="Lecture",
    )
    lecture_synoptic = FloatField(
        blank=False, null=False,
        validators=[
            MinValueValidator(0.0),
        ],
        verbose_name="Synoptic lecture",
    )
    problems_class = FloatField(
        blank=False, null=False,
        validators=[
            MinValueValidator(0.0),
        ],
        verbose_name="Problem class",
    )
    exam = FloatField(
        blank=False, null=False,
        validators=[
            MinValueValidator(0.0),
        ],
        verbose_name="Exam",
    ),
    placement = FloatField(
        blank=False, null=False,
        validators=[
            MinValueValidator(0.0),
        ],
        verbose_name="Student on placement",
    )
    coursework = FloatField(
        blank=False, null=False,
        validators=[
            MinValueValidator(0.0),
        ],
        verbose_name="Coursework",
    )
    misc = FloatField(
        blank=False, null=False,
        validators=[
            MinValueValidator(0.0),
        ],
        verbose_name="Misc",
    )
    year = ForeignKey(
        AcademicYear, blank=False, null=False, on_delete=PROTECT,
        default=get_latest_academic_year,
    )

    def __str__(self):
        return f"Standard Loads ({self.year})"

    class Meta:
        ordering = ('-year',)
        verbose_name = 'Standard Loads'
        verbose_name_plural = 'Standard Loads'