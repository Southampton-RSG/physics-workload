from django.core.validators import MinValueValidator
from django.db.models import Model, ForeignKey, PROTECT, IntegerField, TextField
from django.urls import reverse_lazy

from app.models.module import Module
from app.models.academic_year import AcademicYear
from app.models.dissertation_load_function import DissertationLoadFunction
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
        null=True, blank=True, verbose_name="Credit Hours",
    )

    lectures = IntegerField(
        default=0, verbose_name="Lectures",
    )
    problem_classes = IntegerField(
        default=0, verbose_name="Problem Classes",
    )
    courseworks = IntegerField(
        default=0, verbose_name="Coursework Set",
    )
    synoptic_lectures = IntegerField(
        default=0, verbose_name="Synoptic Lectures",
    )
    exams = IntegerField(
        default=0, verbose_name="Exams",
    )
    dissertation_load_function = ForeignKey(
        DissertationLoadFunction, null=True, blank=True, on_delete=PROTECT,
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

    def get_exam_coverage(self) -> float:
        coverage: float = 0
        for task in self.taskyearmodule_set:
            coverage += task.exam_coverage * task.assignment_set.count()
        return coverage

    def get_problem_class_coverage(self) -> float:
        coverage: float = 0
        for task in self.taskyearmodule_set:
            coverage += task.problem_class_coverage * task.assignment_set.count()
        return coverage

    def get_lecture_coverage(self) -> float:
        coverage: float = 0
        for task in self.taskyearmodule_set:
            coverage += task.lecture_coverage * task.assignment_set.count()
        return coverage

    def get_synoptic_lecture_coverage(self) -> float:
        coverage: float = 0
        for task in self.taskyearmodule_set:
            coverage += task.synoptic_lecture_coverage * task.assignment_set.count()
        return coverage

    def get_dissertation_coverage(self) -> float:
        coverage: float = 0
        for task in self.taskyearmodule_set:
            coverage += task.dissertation_coverage * task.assignment_set.count()
        return coverage

    def get_placement_coverage(self) -> float:
        coverage: float = 0
        for task in self.taskyearmodule_set:
            coverage += task.placement_coverage * task.assignment_set.count()
        return coverage

    def get_absolute_url(self) -> str:
        return reverse_lazy('module_year_detail', args=[self.pk])