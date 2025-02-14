from django.db.models import Model, ForeignKey, PROTECT, TextField, BooleanField
from django.urls import reverse_lazy
from app.models.task_module import TaskModule
from app.models.task_department import TaskDepartment
from app.models.staff_year import StaffYear
from app.models.academic_year import get_latest_academic_year


class AssignmentDepartment(Model):
    """
    Pairs a Staff member up with the task they're performing.
    """
    task_department = ForeignKey(
        TaskDepartment, blank=False, null=False, on_delete=PROTECT,
    )
    staff_year = ForeignKey(
        StaffYear, blank=False, null=False, on_delete=PROTECT,
        limit_choices_to={
            'academic_year': get_latest_academic_year,
        },
    )

    notes = TextField(blank=True)

    is_first_time = BooleanField(default=False)
    is_provisional = BooleanField(default=False)

    class Meta:
        unique_together = ('task_department', 'staff_year')
        ordering = ('-staff_year', 'task_department')
        verbose_name = 'Assignment'
        verbose_name_plural = 'Assignments'

    def __str__(self) -> str:
        return f"{self.task_department} - {self.staff_year}"

    @property
    def load(self) -> float:
        """
        :return: Returns the load for this assignment, with the first-time multiplier if appropriate
        """
        if self.is_first_time:
            return self.task_department.load_first
        else:
            return self.task_department.load

    # def get_absolute_url(self) -> str:
    #     return reverse_lazy('assignment_department_detail', args=[self.pk])

class AssignmentModule(Model):
    """
    Pairs a Staff member up with the task they're performing.
    """
    task_module = ForeignKey(
        TaskModule, blank=False, null=False, on_delete=PROTECT,
    )
    staff_year = ForeignKey(
        StaffYear, blank=False, null=False, on_delete=PROTECT,
        limit_choices_to={
            'academic_year': get_latest_academic_year,
        },
    )

    notes = TextField(blank=True)

    is_first_time = BooleanField(default=False)
    is_provisional = BooleanField(default=False)

    class Meta:
        unique_together = ('task_module', 'staff_year')
        ordering = ('-staff_year', 'task_module')
        verbose_name = 'Assignment'
        verbose_name_plural = 'Assignments'


    def __str__(self) -> str:
        return f"{self.task_module} - {self.staff_year}"

    @property
    def load(self) -> float:
        """
        :return: Returns the load for this assignment, with the first-time multiplier if appropriate
        """
        if self.is_first_time:
            return self.task_module.load_first
        else:
            return self.task_module.load

    # def get_absolute_url(self) -> str:
    #     return reverse_lazy('assignment_department_detail', args=[self.pk])