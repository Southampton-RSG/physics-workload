from django.db.models import Manager
from model_utils.managers import InheritanceManager


class ActiveManager(Manager):
    """
    Custom common manager to filter a model to only show active objects.
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class ActiveInheritanceManager(InheritanceManager):
    """
    Custom common manager to filter a model to only show active objects.
    Needed for polymorphic models (e.g. Tasks).
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)