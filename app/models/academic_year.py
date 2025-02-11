from django.core.validators import MinValueValidator
from django.db.models import Model, IntegerField, FloatField, TextField
from django.urls import reverse_lazy
from django.conf import settings


class AcademicYear(Model):
    """
    Academic year, and the associated standard loads for that year.

    Named AcademicYear as it spans 2 calendar years,
    and to avoid any collisions with base Python year classes.
    """
    year = IntegerField(
        unique=True,
        validators=[
            MinValueValidator(settings.YEAR_MINIMUM_VALUE),
        ],
        help_text="Initial year, e.g. 2000 for 2000-2001 academic year."
    )

    load_per_lecture = FloatField(
        blank=False, null=False,
        validators=[
            MinValueValidator(0.0),
        ],
        verbose_name="Load hours per lecture",
    )
    load_per_synoptic_lecture = FloatField(
        blank=False, null=False,
        validators=[
            MinValueValidator(0.0),
        ],
        verbose_name="Load hours per synoptic lecture",
    )
    load_per_problems_class = FloatField(
        blank=False, null=False,
        validators=[
            MinValueValidator(0.0),
        ],
        verbose_name="Load hours per problem class",
    )
    load_per_exam = FloatField(
        blank=False, null=False,
        validators=[
            MinValueValidator(0.0),
        ],
        verbose_name="Load hours per exam",
    )
    load_per_placement = FloatField(
        blank=False, null=False,
        validators=[
            MinValueValidator(0.0),
        ],
        verbose_name="Load hours per student on placement",
    )
    load_per_coursework = FloatField(
        blank=False, null=False,
        validators=[
            MinValueValidator(0.0),
        ],
        verbose_name="Load hours per student per coursework",
    )
    load_first_time = FloatField(
        blank=False, null=False,
        validators=[
            MinValueValidator(0.0),
        ],
        verbose_name="Multiplier to effective load for first-time assignment",
    )
    misc_load = FloatField(
        blank=False, null=False,
        validators=[
            MinValueValidator(0.0),
        ],
        verbose_name="Misc",
    )
    notes = TextField(blank=True)

    class Meta:
        get_latest_by = 'year'
        ordering = ['-year']
        verbose_name='Academic Year'
        verbose_name_plural='Academic Years'

    def __str__(self) -> str:
        return f"{self.year-2000}/{self.year-1999}"

    def get_absolute_url(self) -> str:
        return reverse_lazy('academic_year_detail', args=[self.pk])


def get_latest_academic_year() -> AcademicYear:
    return AcademicYear.objects.latest()
