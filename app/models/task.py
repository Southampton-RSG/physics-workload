# -*- encoding: utf-8 -*-
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Model, CharField, BooleanField, TextField, IntegerField, ForeignKey, FloatField, Manager
from django.db.models.deletion import PROTECT
from model_utils.managers import InheritanceManager

from app.models.staff import Staff
from app.models.module import Module, DissertationLoadFunction, ModuleYear
from app.models.academic_year import AcademicYear, get_latest_academic_year
from app.models.standard_loads import StandardLoads
from app.models.managers import ActiveManager, ActiveInheritanceManager


class Task(Model):
    """

    """
    module = ForeignKey(
        Module, blank=True, null=True, on_delete=PROTECT,
    )

    name = CharField(max_length=128, blank=False)
    description = TextField(blank=False)
    is_active = BooleanField(default=True)

    objects_active = ActiveInheritanceManager()
    objects = InheritanceManager()

    def __str__(self):
        if self.module:
            return f"{self.module.code} - {self.name}"
        else:
            return f"{self.name}"

    class Meta:
        ordering = ('is_active', 'module', 'name',)
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'


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
    year = ForeignKey(
        AcademicYear, blank=False, null=False, on_delete=PROTECT,
        default=get_latest_academic_year,
    )
    notes = TextField(blank=True)

    class Meta:
        # abstract = True  Can't be abstract or InheritanceManager doesn't work
        get_latest_by = 'year'
        ordering = ('-year', 'task')
        verbose_name = 'ABSTRACT Task Year'
        verbose_name_plural = 'ABSTRACT Task Years'

    def __str__(self):
        """If this task has a subtitle, e.g. Main, then include that in the name"""
        if self.name:
            return f"{self.task}, {self.name} ({self.year})"
        else:
            return f"{self.task} ({self.year})"

    def calculate_load_hours(self, students: int|None = None) -> float:
        """

        :param students:
        :return:
        """
        raise NotImplementedError("Abstract method not implemented")


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
        help_text="Will inherit the number of students on the module this year if not specified",
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
            return self.students * self.load_per_student + self.load_fixed
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
    lecture_synoptic_fraction = FloatField(
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

        :return: The calculated total load for this module
        """
        load: float = 0
        module_year: ModuleYear = self.module_year
        standard_loads: StandardLoads = StandardLoads.objects.get(year=module_year.year)

        if not (students := self.students):
            students = self.module_year.students

        load += standard_loads.lecture * self.module_year.lectures
        load += standard_loads.lecture_synoptic * self.module_year.lectures_synoptic
        load += students * (
            standard_loads.exam * self.module_year.exams +
            standard_loads.problems_class * self.module_year.problem_classes +
            standard_loads.coursework * self.module_year.courseworks
        )

        if self.module_year.module.has_dissertation:
            if self.module_year.dissertation_load_function:
                load += self.dissertation_fraction * self.module_year.dissertation_load_function.calculate(self.students)
            else:
                raise Exception("No dissertation load function")

        return load



class Assignment(Model):
    """

    """
    task_year = ForeignKey(TaskYearBase, on_delete=PROTECT)
    staff = ForeignKey(Staff, on_delete=PROTECT)

    notes = TextField(blank=True)

    is_first_time = BooleanField(default=False)
    is_provisional = BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.task_year} - {self.staff}"

    class Meta:
        unique_together = ('task_year', 'staff')
        ordering = ('-task_year', 'staff')
        verbose_name = 'Assignment'
        verbose_name_plural = 'Assignments'
