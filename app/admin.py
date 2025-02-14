# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from django.contrib.admin import ModelAdmin

from app.models import (
    AcademicGroup, Staff, StandardLoad,
    Module,
    TaskModule, TaskSchool,
    AssignmentSchool, AssignmentModule,

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


@admin.register(AssignmentModule)
class AssignmentModuleAdmin(ModelAdmin):
    """
    Admin class for the AssignmentModule model.
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


@admin.register(TaskSchool)
class TaskSchoolAdmin(ModelAdmin):
    """
    Admin class for the TaskSchool model.
    Uses the default settings, but here in case it needs expanding.
    """
    pass


@admin.register(StandardLoad)
class AcademicYearAdmin(ModelAdmin):
    """
    Admin class for the AcademicYear model.
    Uses the default settings, but here in case it needs expanding.
    """
    pass


@admin.register(AssignmentSchool)
class AssignmentSchoolAdmin(ModelAdmin):
    """
    Admin class for the AssignmentSchool model.
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
