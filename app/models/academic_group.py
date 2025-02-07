from django.db.models import Model, CharField, BooleanField, Manager

from app.models.managers import ActiveManager


class AcademicGroup(Model):
    """
    Academic group, e.g. Astro, Theory, QLM...
    """
    name = CharField(max_length=128, unique=True)

    is_active = BooleanField(default=True)
    objects_active = ActiveManager()
    objects = Manager()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name = 'Academic Group'
        verbose_name_plural = 'Academic Groups'