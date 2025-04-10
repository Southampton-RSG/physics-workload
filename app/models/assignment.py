from logging import getLogger
from typing import Type

from django.db.models import Model, ForeignKey, PROTECT, TextField, BooleanField, Index, FloatField, Manager
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from simple_history.models import HistoricForeignKey

from app.models.task import Task
from app.models.staff import Staff
from app.models.common import ModelCommon


logger = getLogger(__name__)


class Assignment(ModelCommon, Model):
    """
    Pairs a Staff member up with the task they're performing.
    """
    icon = 'clipboard'
    url_root = 'assignment'

    task = HistoricForeignKey(
        Task, blank=False, null=False, on_delete=PROTECT,
        related_name='assignment_set',
    )
    staff = HistoricForeignKey(
        Staff, blank=False, null=False, on_delete=PROTECT,
        limit_choices_to={'is_removed': False},
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

    def update_load(self) -> bool:
        """
        Updates the load for this assignment.
        :return: True if the load has changed.
        """
        if self.is_first_time:
            if self.load_calc != self.task.load_calc_first:
                self.load_calc = self.task.load_calc_first
                self.save()
                return True
        else:
            if self.load_calc != self.task.load_calc:
                self.load_calc = self.task.load_calc
                self.save()
                return True

        return False


@receiver(post_delete, sender=Assignment)
def apply_load(
        sender: Type[Assignment], instance: Assignment, **kwargs
):
    """
    When we delete an assignment, we want to update the assigned hours of the linked staff.
    :param instance: The deleted assignment - this no longer exists in the DB, only in memory!
    """
    logger.debug(f"{instance}: Deleted assignment, updating staff")
    instance.staff.update_load_assigned()
    instance.staff.save()
    instance.staff.standard_load.update_target_load_per_fte()
    instance.staff.standard_load.save()
    instance.task = None
    instance.staff = None
    instance.save()

