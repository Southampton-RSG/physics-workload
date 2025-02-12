from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Model, ForeignKey, PROTECT, IntegerField, TextField, FloatField
from django.urls import reverse_lazy

from app.models.module import Module
from app.models.academic_year import AcademicYear
from app.models.academic_year import get_latest_academic_year


class ModuleYear(Model):
    """

    """
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

    class Meta:
        get_latest_by = 'academic_year'
        unique_together = ('module', 'academic_year')
        ordering = ('-academic_year', 'module')
        verbose_name = 'Module Year'
        verbose_name_plural = 'Module Years'

    def __str__(self):
        return f"{self.module} ({self.academic_year})"

    def get_absolute_url(self) -> str:
        return reverse_lazy('module_year_detail', args=[self.pk])

