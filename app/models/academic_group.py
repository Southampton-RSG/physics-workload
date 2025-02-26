from django.db.models import Model, CharField, BooleanField, Manager
from django.urls import reverse_lazy

from app.models.managers import ActiveManager


class AcademicGroup(Model):
    """
    Academic group, e.g. Astro, Theory, QLM...

    Named AcademicGroup to avoid collision with base Django Group,
    which is more about user permissions.
    """
    icon = "user-group"
    url_root = "academic_group"

    code = CharField(max_length=1, unique=True, blank=False)
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

    def get_absolute_url(self) -> str:
        return reverse_lazy(AcademicGroup.url_root+'_detail', args=[self.code])

    def get_title(self) -> str:
        return f"<i class='fa-solid fa-{self.icon}'></i> <a href='{self.get_absolute_url()}'>{self}</a>"

    @staticmethod
    def get_model_url() -> str:
        return reverse_lazy(AcademicGroup.url_root+'_list')

    @staticmethod
    def get_model_title() -> str:
        return f"<i class='fa-solid fa-{AcademicGroup.icon}'></i> <a href='{AcademicGroup.get_model_url()}'>{AcademicGroup._meta.verbose_name_plural.title()}</a>"
