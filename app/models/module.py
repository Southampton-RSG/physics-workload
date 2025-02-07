# -*- encoding: utf-8 -*-
from django.core.validators import MinValueValidator
from django.db.models import Model, CharField, BooleanField, TextField, IntegerField, ForeignKey, Index
from django.db.models.deletion import PROTECT
from django.db.models.manager import Manager

from app.models.academic_group import AcademicGroup
from app.models.managers import ActiveManager
from app.models.standard_loads import StandardLoads
from app.models.academic_year import AcademicYear, get_latest_academic_year


class DissertationLoadFunction(Model):
    """

    """
    name = CharField(
        max_length=128, unique=True
    )
    expression = TextField(
        blank=False, verbose_name="Weighting Expression"
    )
    is_active = BooleanField(default=True)
    objects_active = ActiveManager()
    objects = ActiveManager()

    def __str__(self) -> str:
        return f"{self.name}"

    class Meta:
        ordering = ('name',)
        verbose_name = 'Dissertation Load Function'
        verbose_name_plural = 'Dissertation Load Functions'

    def calculate(self, students: int) -> float:
        """

        :param students:
        :return:
        """
        return students * 1


class Module(Model):
    """

    """
    name = CharField(max_length=128, blank=False, unique=True)
    code = CharField(max_length=16, blank=False, unique=True)
    notes = TextField(blank=True)

    has_dissertation = BooleanField(default=False)
    has_placement = BooleanField(default=False)

    is_active = BooleanField(default=True)
    objects_active = ActiveManager()
    objects = Manager()

    group = ForeignKey(
        AcademicGroup,
        on_delete=PROTECT,
    )

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"

    class Meta:
        indexes = [
            Index(fields=['code']),
        ]
        ordering = ['name']
        verbose_name = 'Module'
        verbose_name_plural = 'Modules'


class ModuleYear(Model):
    """

    """
    module = ForeignKey(
        Module, blank=False, null=False, on_delete=PROTECT,
        related_name='module_years',
    )
    year = ForeignKey(
        AcademicYear, blank=False, null=False, on_delete=PROTECT,
        default=get_latest_academic_year,
    )
    students = IntegerField(
        null=True, blank=True, default=None, validators=[MinValueValidator(0)]
    )
    credit_hours = IntegerField(
        null=True, blank=True, verbose_name="Credit Hours"
    )

    lectures = IntegerField(
        default=0, verbose_name="Lectures"
    )
    problem_classes = IntegerField(
        default=0, verbose_name="Problem Classes"
    )
    courseworks = IntegerField(
        default=0, verbose_name="Coursework Set"
    )
    lectures_synoptic = IntegerField(
        default=0, verbose_name="Synoptic Lectures"
    )
    exams = IntegerField(
        default=0, verbose_name="Exams"
    )
    dissertation_load_function = ForeignKey(
        DissertationLoadFunction, null=True, blank=True, on_delete=PROTECT
    )

    notes = TextField(blank=True)

    def __str__(self):
        return f"{self.module} ({self.year})"

    class Meta:
        get_latest_by = 'year'
        unique_together = ('module', 'year')
        ordering = ('-year', 'module')
        verbose_name = 'Module Year'
        verbose_name_plural = 'Module Years'

    def calculate_load_hours(self) -> float:
        """

        :return: The calculated total load for this module
        """
        standard_loads: StandardLoads = StandardLoads.objects.latest()
        load: float = 0
        load += standard_loads.lecture * self.lectures
        load += standard_loads.lecture_synoptic * self.lectures_synoptic

        load += standard_loads.exam * self.exams * self.students
        load += standard_loads.problems_class * self.problem_classes * self.students
        load += standard_loads.coursework * self.courseworks * self.students
        if self.module.has_dissertation:
            if self.dissertation_load_function:
                load += self.dissertation_load_function.calculate(self.students)
            else:
                raise Exception("No dissertation load function")

        return load
