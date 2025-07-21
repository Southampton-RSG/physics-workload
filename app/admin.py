from django.contrib import admin
from django.contrib.admin import ModelAdmin

from app.models import (
    AcademicGroup,
    Assignment,
    Staff,
    StandardLoad,
    Task,
    Unit,
)


@admin.register(AcademicGroup)
class AcademicGroupAdmin(ModelAdmin):
    """
    Admin class for the AcademicGroup model.
    Uses the default settings, but here in case it needs expanding.
    """
    pass


@admin.register(Unit)
class UnitAdmin(ModelAdmin):
    """
    Admin class for the Unit model.
    Uses the default settings, but here in case it needs expanding.
    """
    pass


@admin.register(Assignment)
class AssignmentAdmin(ModelAdmin):
    """
    Admin class for the Assignment model.
    Uses the default settings, but here in case it needs expanding.
    """
    pass


@admin.register(Task)
class TaskAdmin(ModelAdmin):
    """
    Admin class for the Task model.
    Uses the default settings, but here in case it needs expanding.
    """
    pass


@admin.register(StandardLoad)
class StandardLoadAdmin(ModelAdmin):
    """
    Admin class for the StandardLoad model.
    Uses the default settings, but here in case it needs expanding.
    """
    pass


@admin.register(Staff)
class StaffAdmin(ModelAdmin):
    """
    Admin class for the Staff model.
    Uses the default settings, but here in case it needs expanding.
    """
    pass
