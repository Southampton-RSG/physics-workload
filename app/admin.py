# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from django.contrib.admin import ModelAdmin

from app.models import (
    AcademicGroup, AcademicYear,
    Module, ModuleYear,
    TaskModule, TaskDepartment,
    TaskYearDepartment, TaskYearModule, Assignment,
    StaffYear, Staff,
)


@admin.register(AcademicGroup)
class AcademicGroupAdmin(ModelAdmin):
    """
    Admin class for the AcademicGroup model.
    Uses the default settings, but here in case it needs expanding.
    """
    pass


@admin.register(Module)
class ModuleAdmin(ModelAdmin):
    """
    Admin class for the Module model.
    Uses the default settings, but here in case it needs expanding.
    """
    pass


@admin.register(ModuleYear)
class ModuleYearAdmin(ModelAdmin):
    """
    Admin class for the ModuleYear model.
    Uses the default settings, but here in case it needs expanding.
    """
    pass


@admin.register(TaskModule)
class TaskModuleAdmin(ModelAdmin):
    """
    Admin class for the TaskModule model.
    Uses the default settings, but here in case it needs expanding.
    """
    pass


@admin.register(TaskDepartment)
class TaskDepartmentAdmin(ModelAdmin):
    """
    Admin class for the TaskDepartment model.
    Uses the default settings, but here in case it needs expanding.
    """
    pass


@admin.register(TaskYearDepartment)
class TaskYearDepartmentAdmin(ModelAdmin):
    """
    Admin class for the TaskYearDepartment model.
    Uses the default settings, but here in case it needs expanding.
    """
    pass


@admin.register(TaskYearModule)
class TaskYearModuleAdmin(ModelAdmin):
    """
    Admin class for the TaskYear model.
    Uses the default settings, but here in case it needs expanding.
    """
    pass


@admin.register(AcademicYear)
class AcademicYearAdmin(ModelAdmin):
    """
    Admin class for the AcademicYear model.
    Uses the default settings, but here in case it needs expanding.
    """
    pass


@admin.register(Assignment)
class AssignmentYearAdmin(ModelAdmin):
    """
    Admin class for the Assignment model.
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


@admin.register(StaffYear)
class StaffYearAdmin(ModelAdmin):
    """
    Admin class for the StaffYear model.
    Uses the default settings, but here in case it needs expanding.
    """
    pass
