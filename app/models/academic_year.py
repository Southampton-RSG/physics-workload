from django.core.validators import MinValueValidator
from django.db.models import Model, IntegerField
from django.conf import settings


class AcademicYear(Model):
    year = IntegerField(
        unique=True,
        validators=[
            MinValueValidator(settings.YEAR_MINIMUM_VALUE),
        ],
        help_text="Initial year, e.g. 2000 for 2000-2001 academic year."
    )

    def __str__(self) -> str:
        return f"{self.year-2000}/{self.year-1999}"

    class Meta:
        get_latest_by = 'year'
        ordering = ['-year']
        verbose_name='Academic Year'
        verbose_name_plural='Academic Years'


def get_latest_academic_year() -> AcademicYear:
    return AcademicYear.objects.latest()
