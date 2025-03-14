from logging import getLogger
from typing import Type

from django.db.models import Model, ForeignKey, PROTECT, TextField, BooleanField, Index, FloatField
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from app.models.task import Task
from app.models.staff import Staff
from app.models.mixins import ModelCommonMixin


logger = getLogger(__name__)


class Assignment(ModelCommonMixin, Model):
    """
    Pairs a Staff member up with the task they're performing.
    """
    icon = 'clipboard'
    url_root = 'assignment'

    task = ForeignKey(
        Task, blank=False, null=False, on_delete=PROTECT,
        related_name='assignment_set',
    )
    staff = ForeignKey(
        Staff, blank=False, null=False, on_delete=PROTECT,
        limit_choices_to={'is_active': True},
        related_name='assignment_set',
    )

    notes = TextField(blank=True)

    is_first_time = BooleanField(default=False)
    is_provisional = BooleanField(default=False)

    load_calc = FloatField(
        default=0.0,
        verbose_name='Load',
    )

    class Meta:
        indexes = [
            Index(fields=['staff']),
            Index(fields=['task']),
        ]
        unique_together = ('task', 'staff')
        ordering = ('-staff', 'task')
        verbose_name = 'Assignment'
        verbose_name_plural = 'Assignments'

    def __str__(self) -> str:
        return f"{self.task.get_name()} - {self.staff.name} [{self.load_calc}]"

    def get_full_name(self):
        return f"{self.task.get_name()} - {self.staff.name}"

    def get_absolute_url(self) -> str:
        """
        :return The absolute URL of the task this assignment belongs to:
        """
        return self.task.get_absolute_url()


@receiver(pre_save, sender=Assignment)
def calculate_load(
        sender: Type[Assignment], instance: Assignment, **kwargs
):
    """
    Called before an assignment is saved, applies the correct load.
    """
    if instance.is_first_time:
        instance.load_calc = instance.task.load_calc_first
    else:
        instance.load_calc = instance.task.load_calc


@receiver(post_save, sender=Assignment)
def apply_load(
        sender: Type[Assignment], instance: Assignment, **kwargs
):
    """
    Called after an assignment is updated - updates the load on all linked staff.
    """
    logger.debug(f"{instance}: Saved assignment, updating staff")
    instance.staff.calculate_load_balance()

@receiver(post_delete, sender=Assignment)
def apply_load(
        sender: Type[Assignment], instance: Assignment, **kwargs
):
    """
    Called after an assignment is updated - updates the load on all linked staff.
    """
    logger.debug(f"{instance}: Deleted assignment, updating staff")
    instance.staff.calculate_load_balance()