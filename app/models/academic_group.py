from django.db.models import Model, CharField, BooleanField, Manager
from django.urls import reverse_lazy

from app.models.managers import ActiveManager
from app.models.mixins import ModelIconMixin


class AcademicGroup(ModelIconMixin, Model):
    """
    Academic group, e.g. Astro, Theory, QLM...

    Named AcademicGroup to avoid collision with base Django Group,
    which is more about user permissions.
    """
    icon = "user-group"
    url_root = "academic_group"

    code = CharField(max_length=1, unique=True, blank=False, primary_key=True)
    name = CharField(max_length=128, unique=True, blank=False)

    is_active = BooleanField(default=True)
    objects_active = ActiveManager()
    objects = Manager()

    class Meta:
        ordering = ('name',)
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'

    def __str__(self):
        return self.name
