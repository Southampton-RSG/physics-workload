# -*- encoding: utf-8 -*-
from django.core.validators import MinValueValidator
from django.db.models import Model, ForeignKey, PROTECT, CharField, FloatField, TextField, IntegerField, BooleanField, Manager
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.urls import reverse_lazy
from simple_history.models import HistoricalRecords
from model_utils.managers import QueryManager

from app.models.load_function import LoadFunction


class TaskDepartment(Model):
    """
    This is the model for tasks that don't belong to a module
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

    notes = TextField(blank=True)


    class Meta:
        ordering = ('is_active', 'name',)
        verbose_name = 'Departmental Task'
        verbose_name_plural = 'Departmental Tasks'

    def __str__(self):
       return f"{self.name}"

    def get_absolute_url(self) -> str:
        return reverse_lazy('task_department', args=[self.pk])


@receiver(pre_save, sender=TaskDepartment)
def calculate_load_for_task_department(sender: TaskDepartment, **kwargs):
    """

    :param sender:
    :param kwargs:
    :return:
    """
    load: float = 0

    if sender.load_function:
        try:
            load += sender.load_function.calculate(sender.students)
        except Exception as calculation_exception:
            raise calculation_exception

    if sender.load_fixed_first:
        sender.load_calc_first = sender.load_fixed_first + load
    else:
        sender.load_calc_first = sender.load_fixed + load

    sender.load = sender.load_fixed + load
