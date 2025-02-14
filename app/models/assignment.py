from django.db.models import Model, ForeignKey, PROTECT, TextField, BooleanField
from django.urls import reverse_lazy
from app.models.task_module import TaskModule
from app.models.task_school import TaskSchool
from app.models.staff import Staff
from app.models.standard_load import get_current_standard_load


class AssignmentSchool(Model):
    """
    Pairs a Staff member up with the task they're performing.
    """
    task = ForeignKey(
        TaskSchool, blank=False, null=False, on_delete=PROTECT,
    )
    staff = ForeignKey(
        Staff, blank=False, null=False, on_delete=PROTECT,
        limit_choices_to={'is_active': True},
    )

    notes = TextField(blank=True)

    is_first_time = BooleanField(default=False)
    is_provisional = BooleanField(default=False)

    class Meta:
        unique_together = ('task', 'staff')
        ordering = ('-staff', 'task')
        verbose_name = 'School Assignment'
        verbose_name_plural = 'School Assignments'

    def __str__(self) -> str:
        return f"{self.task} - {self.staff}"

    @property
    def load(self) -> float:
        """
        :return: Returns the load for this assignment, with the first-time multiplier if appropriate
        """
        if self.is_first_time:
            return self.task.load_first
        else:
            return self.task.load

    # def get_absolute_url(self) -> str:
    #     return reverse_lazy('assignment_department_detail', args=[self.pk])


class AssignmentModule(Model):
    """
    Pairs a Staff member up with the task they're performing.
    """
    task= ForeignKey(
        TaskModule, blank=False, null=False, on_delete=PROTECT,
    )
    staff = ForeignKey(
        Staff, blank=False, null=False, on_delete=PROTECT,
        limit_choices_to={'is_active': True},
    )

    notes = TextField(blank=True)

    is_first_time = BooleanField(default=False)
    is_provisional = BooleanField(default=False)

    class Meta:
        unique_together = ('task', 'staff')
        ordering = ('-staff', 'task')
        verbose_name = 'Module Assignment'
        verbose_name_plural = 'Module Assignments'


    def __str__(self) -> str:
        return f"{self.task} - {self.staff}"

    @property
    def load(self) -> float:
        """
        :return: Returns the load for this assignment, with the first-time multiplier if appropriate
        """
        if self.is_first_time:
            return self.task.load_first
        else:
            return self.task.load

    # def get_absolute_url(self) -> str:
    #     return reverse_lazy('assignment_department_detail', args=[self.pk])