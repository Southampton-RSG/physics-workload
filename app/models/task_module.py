# -*- encoding: utf-8 -*-
from django.core.validators import MinValueValidator
from django.db.models import Model, ForeignKey, PROTECT, CharField, FloatField, TextField, IntegerField, BooleanField, Manager
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.urls import reverse_lazy
from model_utils.managers import QueryManager
from simple_history.models import HistoricalRecords

from app.models.academic_year import AcademicYear, get_latest_academic_year
from app.models.load_function import LoadFunction
from app.models.module import Module
from app.models.task_department import calculate_load_for_task_department


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
        verbose_name="Fixed load hours (first time)",
    )

    # === CACHED LOADS ===
    load = FloatField(
        default=0.0, validators=[MinValueValidator(0.0)], blank=False, null=False,
    )
    load_first = FloatField(
        default=0.0, validators=[MinValueValidator(0.0)], blank=False, null=False,
    )

    load_function = ForeignKey(
        LoadFunction, blank=False, null=False, on_delete=PROTECT,
        help_text="Function by which student load for this task scales",
    )
    students = IntegerField(
        null=True, blank=True,
        help_text="Number of students for scaling load",
    )

    module = ForeignKey(
        Module, blank=False, null=False, on_delete=PROTECT,
    )

    notes = TextField(blank=True)

    class Meta:
        ordering = ('is_active', 'module', 'name',)
        verbose_name = 'Module Task'
        verbose_name_plural = 'Module Tasks'

    def __str__(self):
       return f"{self.module.code} - {self.name}"

    def get_absolute_url(self) -> str:
        return reverse_lazy('module', args=[self.pk])


receiver(pre_save, sender=TaskModule)
def calculate_load_for_task_year_module(sender: TaskModule, **kwargs):
    """

    :return:
    """
    if not (sender.coursework_fraction or sender.exam_fraction):
        calculate_load_for_task_department(sender, **kwargs)

    else:
        # SPREADSHEET LOGIC
        academic_year: AcademicYear = get_latest_academic_year()
        module: Module = sender.module

        # ($I2+$Q2) = "Number of Lectures/Problem Classes Run by Coordinator" + "Number of Synoptic Lectures"
        contact_sessions: int = module.lectures + module.synoptic_lectures + module.problem_classes

        # (($I2+$Q2)*3.5) or (($I2+$Q2)*6)
        load_lecture: float = contact_sessions * academic_year.load_lecture
        load_lecture_first: float = contact_sessions * academic_year.load_lecture_first

        # ($J2*2) = "Coursework (number of items prepared)"
        load_coursework_set: float = module.coursework * academic_year.load_coursework_set
        # ($L2*$O2*2) = "Coursework (fraction of module mark)" * "Total Number of CATS"
        load_coursework_credit: float = module.coursework_mark_fraction * module.credit_hours * academic_year.load_coursework_credit

        # ($J2+$L2*$Q2) = "Coursework (number of items prepared)" + "Coursework (fraction of module mark)" * "Total Number of CATS"
        # (0.1667 * [] * $K2 * $P2) = "Fraction of Coursework marked by coordinator" * "Number of Students"
        load_coursework_marked: float = (module.coursework + sender.coursework_fraction * module.credit_hours) * \
            sender.coursework_fraction * module.students * academic_year.load_coursework_marked

        # ($M2*O2*2) = "Examination (fraction of module mark)" * "Total Number of CATS"
        load_exam_credit: float = sender.exam_fraction * module.credit_hours * academic_year.load_exam_credit

        # ($P2*$N2*1) = "Number of Students" * "Fraction of Exams Marked by Coordinator"
        load_exam_marked: float = module.students * sender.exam_fraction * academic_year.load_exam_marked

        load: float = load_coursework_set + load_coursework_credit + \
                      load_exam_credit + load_exam_marked + load_coursework_marked

        if module.has_dissertation:
            if sender.load_function:
                load += sender.load_function.calculate(sender.students)
            else:
                raise Exception("No dissertation load function")

        sender.load_calc_first = load + sender.load_fixed_first + load_lecture_first
        sender.load_calc = load + sender.load_fixed + load_lecture
