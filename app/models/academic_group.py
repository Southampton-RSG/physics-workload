from django.db.models import Model, CharField, BooleanField, Manager
from django.urls import reverse_lazy

from app.models.managers import ActiveManager


class AcademicGroup(Model):
    """
    Academic group, e.g. Astro, Theory, QLM...

    Named AcademicGroup to avoid collision with base Django Group,
    which is more about user permissions.
    """
    name = CharField(max_length=128, unique=True)

    is_active = BooleanField(default=True)
    objects_active = ActiveManager()
    objects = Manager()

    class Meta:
        ordering = ('name',)
        verbose_name = 'Academic Group'
        verbose_name_plural = 'Academic Groups'

    def __str__(self):
        return self.name

    def get_absolute_url(self) -> str:
        return reverse_lazy('academic_group_detail', args=[self.pk])
