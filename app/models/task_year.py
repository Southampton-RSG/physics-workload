from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Model, ForeignKey, PROTECT, CharField, FloatField, TextField, IntegerField
from django.urls import reverse_lazy
from model_utils.managers import InheritanceManager

from app.models.task import Task
from app.models.module_year import ModuleYear
from app.models.load_function import LoadFunction
from app.models.academic_year import get_latest_academic_year, AcademicYear


class TaskYearBase(Model):
    """

    """
    task = ForeignKey(
        Task, blank=False, null=False, on_delete=PROTECT,
    )
    name = CharField(
        max_length=128, blank=True,
        help_text="Optional qualifier for the task",
    )
    load_fixed = FloatField(
        default=0.0, validators=[MinValueValidator(0.0)],
        verbose_name="Load hours (fixed)",
    )
    academic_year = ForeignKey(
        AcademicYear, blank=False, null=False, on_delete=PROTECT,
        default=get_latest_academic_year,
    )
    notes = TextField(blank=True)

    objects = InheritanceManager()

    class Meta:
        # abstract = True  Can't be abstract or InheritanceManager doesn't work
        get_latest_by = 'academic_year'
        ordering = ('-academic_year', 'task')
        verbose_name = 'Task Year'
        verbose_name_plural = 'Task Year'

    def __str__(self) -> str:
        return f"{self.task} ({self.academic_year})"

    @property
    def load(self) -> float:
        """
        :return: Returns the load for this task
        """
        return self.load_fixed

    @property
    def load_first(self) -> float:
        """
        :return: Returns the load for this task
        """
        return self.load



class TaskYearScaling(TaskYearBase):
    """

    """
    load_function = ForeignKey(
        LoadFunction, blank=False, null=False, on_delete=PROTECT,
        help_text="Function by which load for this task scales",
    )
    students = IntegerField(
        null=True, blank=True,
        help_text="The number of students served by this task, if any",
    )

    class Meta:
        verbose_name = 'Scaling Task'
        verbose_name_plural = 'Scaling Tasks'

    @property
    def load(self) -> float:
        """
        :return: Returns the load for this task
        """
        return self.load_fixed + self.load_function.calculate(self.students)

    @property
    def load_first(self) -> float:
        """
        :return: Returns the load for this task
        """
        return self.load


class TaskYearModule(TaskYearBase):
    """

    """
    module_year = ForeignKey(
        ModuleYear, blank=False, null=False, on_delete=PROTECT,
    )
    coursework_fraction = FloatField(
        default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="Fraction of module coursework marked",
    )
    exam_fraction = FloatField(
        default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="Fraction of module exams marked",
    )

    class Meta:
        get_latest_by = 'module_year'
        ordering = ('-module_year', 'task')
        verbose_name = 'Module Task'
        verbose_name_plural = 'Module Tasks'


    @property
    def load(self) -> float:
        """
        :return: Returns the load for this task
        """
        return self.load_fixed

    @property
    def load_first(self) -> float:
        """
        :return: Returns the load for this task
        """
        return self.load