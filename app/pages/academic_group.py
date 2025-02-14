"""
Handles the views for the Academic Groups
"""
from django.urls import path
from django.utils.html import format_html, mark_safe
from django.template import Template

from iommi import Page, Table, html, Form, EditTable, Column
from iommi.path import register_path_decoding
from iommi import register_search_fields
from iommi.views import crud_views

from app.models import AcademicGroup, Staff, Module, TaskModule
from app.pages import BasePage


register_path_decoding(academic_group=lambda string, **_: AcademicGroup.objects.get(code=string))


class AcademicGroupDetail(BasePage):
    """

    """
    title = html.h1(lambda params, **_: f"{params.academic_group}")

    staff = Table(
        auto__model=Staff,
        auto__include=['name', 'load_balance', 'assignmentschool_set', 'assignmentmodule_set'],
        columns__assignmentschool_set__display_name="School",
        columns__assignmentschool_set__group="Assignments",
        columns__assignmentmodule_set__display_name="Module",
        columns__assignmentmodule_set__group="Assignments",
        rows=lambda params, **_: Staff.objects_active.filter(academic_group=params.academic_group),
        columns__name__cell__url = lambda row, **_: row.get_absolute_url(),
        page_size=20,
    )
    modules = Table(
        auto__model=Module,
        auto__include=['code', 'name', 'taskmodule_set', 'students'],
        columns__code__cell__url=lambda row, **_: row.get_absolute_url(),
        columns__name__cell__url=lambda row, **_: row.get_absolute_url(),
        columns__taskmodule_set={
            "display_name": 'Module Tasks',
            "cell__template": 'app/academic_group/module_task_cell.html',
        },
        rows=lambda params, **_: Module.objects_active.filter(academic_group=params.academic_group),
        page_size=20,
    )


class AcademicGroupEdit(BasePage):
    """

    """
    form = Form.edit(
        title=lambda params, **_: f"{params.academic_group} / Edit",
        auto__model=AcademicGroup, instance=lambda params, **_: params.academic_group, editable=True,
        fields__code__group="row1",
        fields__name__group="row1",
    )


class AcademicGroupList(BasePage):
    """
    Page listing the academic groups
    """
    groups = Table(
        auto__model=AcademicGroup,
        auto__include=['name'],
        columns__staff=Column(
            cell__value=lambda row, **_: row.staff_set.count(),
        ),
        columns__modules=Column(
            cell__value=lambda row, **_: row.module_set.count(),
        ),
        columns__name__cell__url=lambda row, **_: row.get_absolute_url(),
        columns__edit=Column.edit(
            cell__url=lambda row, **_: f"{row.get_absolute_url()}edit/",
        ),
    )


urlpatterns = [
    path('group/<academic_group>/edit/', AcademicGroupEdit().as_view(), name='academic_group_edit'),
    path('group/<academic_group>/', AcademicGroupDetail().as_view(), name='academic_group_detail'),
    path('group/', AcademicGroupList().as_view(), name='academic_group_list'),
]
