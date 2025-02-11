from django.db.models import Model, ForeignKey, PROTECT, TextField, BooleanField
from django.urls import reverse_lazy
from app.models.task_year import TaskYearBase
from app.models.staff_year import StaffYear
from app.models.academic_year import get_latest_academic_year


class Assignment(Model):
    """
    Pairs a Staff member up with the task they're performing.
    """
    task_year = ForeignKey(
        TaskYearBase, blank=False, null=False, on_delete=PROTECT,
    )
    staff_year = ForeignKey(
        StaffYear, blank=False, null=False, on_delete=PROTECT,
        limit_choices_to={
            'academic_year': get_latest_academic_year,
        },
        related_name='assignments',
    )

    notes = TextField(blank=True)

    is_first_time = BooleanField(default=False)
    is_provisional = BooleanField(default=False)

    class Meta:
        unique_together = ('task_year', 'staff_year')
        ordering = ('-task_year', 'staff_year')
        verbose_name = 'Assignment'
        verbose_name_plural = 'Assignments'

    def __str__(self) -> str:
        return f"{self.task_year} - {self.staff_year}"

    @property
    def load(self) -> float:
        """
        :return: Returns the load for this assignment, with the first-time multiplier if appropriate
        """
        load: float = TaskYearBase.objects.get_subclass(id=self.task_year.id).load
        if self.is_first_time:
            return load * self.task_year.academic_year.load_first_time
        else:
            return load

    def get_absolute_url(self) -> str:
        return reverse_lazy('assignment_detail', args=[self.pk])