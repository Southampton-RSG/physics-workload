from logging import Manager

from django.db.models import Model, ForeignKey, PROTECT, TextField, BooleanField, Index
from django.urls import reverse_lazy
from app.models.task import Task
from app.models.staff import Staff
from app.models.standard_load import get_current_standard_load



class Assignment(Model):
    """
    Pairs a Staff member up with the task they're performing.
    """
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
        return f"{self.task} - {self.staff} [{self.load}]"

    def get_name_for_staff(self) -> str:
        """:return: The name without the staff member"""
        return f"{self.task} [{self.load}]"

    @property
    def load(self) -> float:
        """
        :return: Returns the load for this assignment, with the first-time multiplier if appropriate
        """
        if self.is_first_time:
            return self.task.load_first
        else:
            return self.task.load

    def get_absolute_url(self) -> str:
        return ''
        #return reverse_lazy('assignment_department_detail', args=[self.pk])
