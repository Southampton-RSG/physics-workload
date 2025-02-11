from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Model, ForeignKey, PROTECT, CharField, FloatField, TextField, IntegerField
from django.urls import reverse_lazy
from model_utils.managers import InheritanceManager

from app.models import Task, AcademicYear, ModuleYear
from app.models.academic_year import get_latest_academic_year


class TaskYearBase(Model):
    """

    """
    task = ForeignKey(
        Task, blank=False, null=False, on_delete=PROTECT,
    )
    name = CharField(
        max_length=128, blank=True,
        help_text="Optional qualifier for the task, e.g. 'Main' for 'Demonstrator, Main'.",
    )
    load_fixed = FloatField(
        default=0.0, validators=[MinValueValidator(0.0)],
        verbose_name="Load hours (fixed)",
    )
    load_cache = FloatField(
        null=True, blank=True,
        verbose_name="Cached calculation of load hours",
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
        verbose_name = 'ABSTRACT Task Year'
        verbose_name_plural = 'ABSTRACT Task Years'

    def __str__(self):
        """If this task has a subtitle, e.g. Main, then include that in the name"""
        if self.name:
            return f"{self.task}, {self.name} ({self.academic_year})"
        else:
            return f"{self.task} ({self.academic_year})"

    def calculate_load_hours(self, students: int|None = None) -> float:
        """

        :param students:
        :return:
        """
        raise NotImplementedError("Abstract method not implemented")

    @property
    def load(self) -> float:
        """
        Wrapper that caches the calculation of load for this task
        :return: Returns the load for this task
        """
        if not self.load_cache:
            self.load_cache = self.calculate_load_hours()

        return self.load_cache


class TaskYearGeneral(TaskYearBase):
    """

    """
    load_per_student = FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0.0)],
        verbose_name="Load hours per student",
    )
    students = IntegerField(
        null=True, blank=True,
        help_text="The number of students served by this task, if any",
    )

    class Meta:
        verbose_name = 'Departmental Task'
        verbose_name_plural = 'Departmental Tasks'


    def calculate_load_hours(self, students: int|None = None) -> float:
        """
        Calculates the load hours associated with the task this year

        :param students: Number of students served by this task
        :return: The calculated load hours
        """
        if self.students:
            return self.load_fixed + self.load_per_student * self.students
        else:
            return self.load_fixed


class TaskYearModule(TaskYearBase):
    """

    """
    module_year = ForeignKey(
        ModuleYear, blank=False, null=False, on_delete=PROTECT,
    )
    lecture_fraction = FloatField(
        default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="Fraction of module lectures given",
    )
    synoptic_lecture_fraction = FloatField(
        default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="Fraction of module synoptic lectures given",
    )

    coursework_fraction = FloatField(
        default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="Fraction of module coursework marked",
    )
    problem_class_fraction = FloatField(
        default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="Fraction of module problem classes marked",
    )
    exam_fraction = FloatField(
        default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="Fraction of module exams marked",
    )
    dissertation_fraction = FloatField(
        default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="Fraction of module dissertations marked",
    )
    placement_fraction = FloatField(
        default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="Fraction of module placement responsibilities",
    )

    load_per_student = FloatField(
        default=0.0, validators=[MinValueValidator(0.0)],
        verbose_name="Additional load hours per student",
    )
    students = IntegerField(
        null=True, blank=True,
        help_text="Will inherit the number of students on the module this year if not specified",
    )

    class Meta:
        get_latest_by = 'module_year'
        ordering = ('-module_year', 'task')
        verbose_name = 'Module Task'
        verbose_name_plural = 'Module Tasks'

    def calculate_load_hours(self) -> float:
        """
        Calculates the load hours associated with the task this year

        :param students: Number of students served by this task
        :return: The calculated load hours
        """
        if self.load_cache:
            return self.load_cache

        module_year: ModuleYear = self.module_year
        academic_year: AcademicYear = module_year.academic_year

        if not (students := self.students):
            students: int = self.module_year.students

        load_lecture: float = \
            academic_year.load_per_lecture * self.module_year.lectures * self.lecture_fraction + \
            academic_year.load_per_synoptic_lecture * self.module_year.synoptic_lectures * self.synoptic_lecture_fraction

        load_per_student: float = \
            academic_year.load_per_exam * self.module_year.exams * self.exam_fraction + \
            academic_year.load_per_problems_class * self.module_year.problem_classes * self.problem_class_fraction + \
            academic_year.load_per_coursework * self.module_year.courseworks * self.coursework_fraction + \
            (academic_year.load_per_placement * self.placement_fraction if self.module_year.module.has_dissertation else 0)

        load: float = self.load_fixed + load_lecture + load_per_student * students

        if self.module_year.module.has_dissertation:
            if self.module_year.dissertation_load_function:
                load += self.dissertation_fraction * self.module_year.dissertation_load_function.calculate(self.students)
            else:
                raise Exception("No dissertation load function")

        return load
