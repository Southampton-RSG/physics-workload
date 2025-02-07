# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from django.contrib.admin import ModelAdmin

from app.models import (
    Transaction, AcademicGroup, AcademicYear, StandardLoads,
    Module, ModuleYear,
    Task, TaskYearGeneral, TaskYearModule, Assignment,
    StaffYear, Staff, StaffHours
)
from import_export import resources
from import_export.admin import ImportMixin, ImportExportModelAdmin


class TransactionResource(resources.ModelResource):
    class Meta:
        model = Transaction
        fields = ['id', 'bill_for', 'issue_date', 'due_date', 'total', 'status', 'created_time']


@admin.register(AcademicGroup)
class AcademicGroupAdmin(ModelAdmin):
    """
    Admin class for the AcademicGroup model.
    Uses the default settings, but here in case it needs expanding.
    """
    pass


@admin.register(StandardLoads)
class StandardLoadsAdmin(ModelAdmin):
    """
    Admin class for the StandardLoads model.
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


@admin.register(Task)
class TaskAdmin(ModelAdmin):
    """
    Admin class for the Task model.
    Uses the default settings, but here in case it needs expanding.
    """
    pass


@admin.register(TaskYearGeneral)
class TaskYearGeneralAdmin(ModelAdmin):
    """
    Admin class for the TaskYear model.
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


@admin.register(StaffHours)
class StaffHoursAdmin(ModelAdmin):
    """
    Admin class for the StaffHours model.
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



@admin.register(Transaction)
class TransactionAdmin(ImportMixin, ModelAdmin):
    list_display = ['id', 'bill_for', 'issue_date', 'due_date', 'total', 'status', 'created_time']
    resource_class = TransactionResource
