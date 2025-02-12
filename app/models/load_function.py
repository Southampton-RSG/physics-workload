from django.db.models import Model, CharField, TextField, BooleanField, Manager
from django.urls import reverse_lazy
from app.models.managers import ActiveManager


class LoadFunction(Model):
    """
    Evaluatable Python expression that determines the load for a number of students,
    e.g. for number of tutees or when marking a dissertation..
    """
    name = CharField(
        max_length=128, unique=True
    )
    expression = TextField(
        blank=False, verbose_name="Weighting Expression"
    )
    is_active = BooleanField(default=True)
    objects_active = ActiveManager()
    objects = Manager()

    notes = TextField(blank=True)

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

    def get_absolute_url(self) -> str:
        return reverse_lazy('dissertation_load_function_detail', args=[self.pk])