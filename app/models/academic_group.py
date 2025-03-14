from django.contrib.auth.models import AbstractUser
from django.db.models import Model, CharField, BooleanField, Manager

from app.models.managers import ActiveManager
from app.models.mixins import ModelCommonMixin


class AcademicGroup(ModelCommonMixin, Model):
    """
    Academic group, e.g. Astro, Theory, QLM...

    Named AcademicGroup to avoid collision with base Django Group,
    which is more about user permissions.
    """
    icon = "users"
    url_root = "academic_group"


    code = CharField(max_length=1, unique=True, blank=False, primary_key=True)
    short_name = CharField(max_length=16, unique=True, blank=False, db_index=True)
    name = CharField(max_length=128, unique=True, blank=False)

    is_active = BooleanField(default=True)
    objects_active = ActiveManager()
    objects = Manager()

    class Meta:
        ordering = ('name',)
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'

    def __str__(self):
        return f"{self.short_name}"

    def get_instance_header(self, text: str|None = None) -> str:
        """Uses the full name for the header of one of these"""
        return super().get_instance_header(text=self.name)

    def has_access(self, user: AbstractUser) -> bool:
        """
        Only users assigned to a task can see the details
        :param user: The user
        :return: True if the user is assigned to this task
        """
        return user.staff.academic_group == self
