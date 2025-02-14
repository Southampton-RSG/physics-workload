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

    load_lecture = FloatField(
        blank=False, null=False,
        validators=[
            MinValueValidator(0.0),
        ],
        verbose_name="Load hours per lecture & problems class",
    )
    load_lecture_first = FloatField(
        blank=False, null=False,
        validators=[
            MinValueValidator(0.0),
        ],
        verbose_name="Load hours per lecture & problems class for first-time assignment",
    )

    load_coursework_set = FloatField(
        blank=False, null=False,
        validators=[
            MinValueValidator(0.0),
        ],
        verbose_name="Load hours per item of coursework prepared",
    )
    load_coursework_credit = FloatField(
        blank=False, null=False,
        validators=[
            MinValueValidator(0.0),
        ],
        verbose_name="Load hours per coursework credit hour",
    )
    load_coursework_marked = FloatField(
        blank=False, null=False,
        validators=[
            MinValueValidator(0.0),
        ],
        verbose_name="Load hours per (coursework plus coursework credit hour) marked",
    )

    load_exam_credit = FloatField(
        blank=False, null=False,
        validators=[
            MinValueValidator(0.0),
        ],
        verbose_name="Load hours per exam credit hour",
    )
    load_exam_marked = FloatField(
        blank=False, null=False,
        validators=[
            MinValueValidator(0.0),
        ],
        verbose_name="Load hours per exam marked",
    )
    load_fte_misc = FloatField(
        blank=False, null=False,
        validators=[
            MinValueValidator(0.0),
        ],
        verbose_name="Staff misc. load per FTE fraction",
    )
    notes = TextField(blank=True)

    class Meta:
        get_latest_by = 'year'
        ordering = ['-year']
        verbose_name='Academic Year'
        verbose_name_plural='Academic Years'

    def __str__(self) -> str:
        return f"{self.year-2000}/{self.year-1999}"

    # def get_absolute_url(self) -> str:
    #     return reverse_lazy('academic_year_detail', args=[self.pk])


def get_latest_academic_year() -> AcademicYear:
    try:
        academic_year: AcademicYear = AcademicYear.objects.latest()
        return academic_year
    except:
        return None
