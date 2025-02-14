# -*- encoding: utf-8 -*-
from typing import Type

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Model, ForeignKey, PROTECT, CharField, FloatField, TextField, IntegerField, BooleanField, Manager
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.urls import reverse_lazy
from model_utils.managers import QueryManager
from simple_history.models import HistoricalRecords

from app.models.standard_load import StandardLoad, get_current_standard_load
from app.models.load_function import LoadFunction
from app.models.module import Module


class TaskModule(Model):
    """
    This is the model for tasks that belong to a module
    """
    name = CharField(max_length=128, blank=False)
    description = TextField(blank=False)

    is_active = BooleanField(default=True)
    objects_active = QueryManager(is_active=True)
    objects = Manager()

    history = HistoricalRecords()

    module = ForeignKey(
        Module, blank=False, null=False, on_delete=PROTECT,
    )
    number_needed = IntegerField(
        null=False, blank=False, default=1,
        validators=[MinValueValidator(1)],
    )

    load_fixed = FloatField(
        default=0.0, validators=[MinValueValidator(0.0)],
        verbose_name="Fixed load hours",
    )
    load_fixed_first = FloatField(
        default=0.0, validators=[MinValueValidator(0.0)], blank=True, null=True,
        verbose_name="Extra load hours for first-time",
    )

    load_function = ForeignKey(
        LoadFunction, blank=True, null=True, on_delete=PROTECT,
        help_text="Function by which student load for this task scales",
    )
    students = IntegerField(
        null=True, blank=True,
        help_text="Number of students for scaling load, if not the whole module",
    )

    coursework_fraction = FloatField(
        default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="Fraction of coursework marked",
    )

    exam_fraction = FloatField(
        default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="Fraction of exams marked",
    )

    notes = TextField(blank=True)

    # === CACHED LOADS ===
    load = FloatField(
        default=0.0, validators=[MinValueValidator(0.0)], blank=False, null=False,
    )
    load_first = FloatField(
        default=0.0, validators=[MinValueValidator(0.0)], blank=False, null=False,
    )

    class Meta:
        ordering = ('is_active', 'module', 'name',)
        verbose_name = 'Module Task'
        verbose_name_plural = 'Module Tasks'

    def __str__(self):
       return f"{self.name}"

    def get_absolute_url(self) -> str:
        # return reverse_lazy('task_module_detail', args=[self.pk])
        return reverse_lazy('module_detail', args=[self.module.pk])


receiver(pre_save, sender=TaskModule)
def calculate_load_for_task_year_module(
        sender: Type[TaskModule], instance: TaskModule, **kwargs
):
    """

    :return:
    """
    if not (instance.coursework_fraction or instance.exam_fraction):
        load: float = 0

        if instance.load_function:
            try:
                load += instance.load_function.calculate(instance.students)
            except Exception as calculation_exception:
                raise calculation_exception

        instance.load = instance.load_fixed + load
        instance.load_first = instance.load + instance.load_fixed_first

    else:
        # SPREADSHEET LOGIC
        standard_load: StandardLoad = get_current_standard_load()
        module: Module = instance.module

        # ($I2+$Q2) = "Number of Lectures/Problem Classes Run by Coordinator" + "Number of Synoptic Lectures"
        contact_sessions: int = module.lectures + module.synoptic_lectures + module.problem_classes

        # (($I2+$Q2)*3.5) or (($I2+$Q2)*6)
        load_lecture: float = contact_sessions * standard_load.load_lecture
        load_lecture_first: float = contact_sessions * standard_load.load_lecture_first

        # ($J2*2) = "Coursework (number of items prepared)"
        load_coursework_set: float = module.coursework * standard_load.load_coursework_set
        # ($L2*$O2*2) = "Coursework (fraction of module mark)" * "Total Number of CATS"
        load_coursework_credit: float = module.coursework_mark_fraction * module.credit_hours * standard_load.load_coursework_credit

        # ($J2+$L2*$Q2) = "Coursework (number of items prepared)" + "Coursework (fraction of module mark)" * "Total Number of CATS"
        # (0.1667 * [] * $K2 * $P2) = "Fraction of Coursework marked by coordinator" * "Number of Students"
        load_coursework_marked: float = (module.coursework + instance.coursework_fraction * module.credit_hours) * \
            instance.coursework_fraction * module.students * standard_load.load_coursework_marked

        # ($M2*O2*2) = "Examination (fraction of module mark)" * "Total Number of CATS"
        load_exam_credit: float = instance.exam_fraction * module.credit_hours * standard_load.load_exam_credit

        # ($P2*$N2*1) = "Number of Students" * "Fraction of Exams Marked by Coordinator"
        load_exam_marked: float = module.students * instance.exam_fraction * standard_load.load_exam_marked

        load: float = load_coursework_set + load_coursework_credit + \
                      load_exam_credit + load_exam_marked + load_coursework_marked
        
        if instance.load_function:
            load += instance.load_function.calculate(instance.students)
        else:
            raise Exception("Task has no load function")

        instance.load_calc_first = load + instance.load_fixed + load_lecture_first + instance.load_fixed_first
        instance.load_calc = load + instance.load_fixed + load_lecture


class TaskModuleField(ForeignKey):
    """
    Semantic model wrapper for the relationship, so Iommi can style it easily:
    https://docs.iommi.rocks/en/latest/semantic_models.html
    """
    def __init__(self, to=None, *args, **kwargs):
        assert to is None
        to = TaskModule
        super().__init__(to=to, *args, **kwargs)
