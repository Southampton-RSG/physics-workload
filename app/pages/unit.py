"""
Pages for academic units
"""
from typing import Dict
from django.contrib.auth.models import AbstractUser, AnonymousUser
from django.urls import path
from django.utils.html import format_html
from django.template import Template, Context
from django.template.loader import render_to_string

from iommi import Page, Field, Header
from iommi.experimental.main_menu import M

from app.forms.task import TaskForm
from app.forms.unit import UnitForm
from app.pages.task import TaskDetail, TaskEdit, TaskDelete
from app.models import Unit, Task
from app.tables.task import TaskTable
from app.tables.unit import UnitTable


class UnitTaskCreate(Page):
    """
    Create a task associated with a unit
    """
    header = Header(
        lambda params, **_: format_html(
            f"{params.unit.get_instance_header()} / Create Task "+render_to_string(
                "app/create_icon.html"
            )
        ),
    )
    form = TaskForm.create(
        h_tag=None,
        fields__unit=Field.non_rendered(
            initial=lambda params, **_: params.unit,
        ),
    )


class UnitDetail(Page):
    """
    View a unit and its associated tasks
    """
    header = Header(
        lambda params, **_: params.unit.get_instance_header()
    )
    tasks = TaskTable(
        h_tag=Header,
        columns__unit_code__include=False,
        query__include=False,
        rows=lambda params, **_: TaskTable.annotate_query_set(params.unit.task_set.filter(is_removed=False).all()),
        columns__assignment_set__cell__template='app/unit/assignment_set.html',
    )
    form = UnitForm(
        title="Details",
        instance=lambda params, **_: params.unit,
        fields__name__include=False,
        fields__code__include=False,
        fields__lectures__include=lambda params, **_: params.unit.lectures,
        fields__problem_classes__include=lambda params, **_: params.unit.problem_classes,
        fields__coursework__include=lambda params, **_: params.unit.coursework,
        fields__synoptic_lectures__include=lambda params, **_: params.unit.synoptic_lectures,
        fields__exams__include=lambda params, **_: params.unit.exams,
        fields__exam_mark_fraction__include=lambda params, **_: params.unit.exam_mark_fraction,
        fields__coursework_mark_fraction__include=lambda params, **_: params.unit.coursework_mark_fraction,
        fields__has_dissertation__include=lambda params, **_: params.unit.has_dissertation,
        fields__has_placement__include=lambda params, **_: params.unit.has_placement,
        editable=False,
    )


class UnitDelete(Page):
    """
    View a unit and its associated tasks
    """
    header = Header(
        lambda params, **_: params.unit.get_instance_header()
    )
    form = UnitForm.delete(
        h_tag=None,
        instance=lambda params, **_: params.unit,
         fields__name__include=False,
        fields__code__include=False,
        fields__lectures__include=lambda params, **_: params.unit.lectures,
        fields__problem_classes__include=lambda params, **_: params.unit.problem_classes,
        fields__coursework__include=lambda params, **_: params.unit.coursework,
        fields__synoptic_lectures__include=lambda params, **_: params.unit.synoptic_lectures,
        fields__exams__include=lambda params, **_: params.unit.exams,
        fields__exam_mark_fraction__include=lambda params, **_: params.unit.exam_mark_fraction,
        fields__coursework_mark_fraction__include=lambda params, **_: params.unit.coursework_mark_fraction,
        fields__has_dissertation__include=lambda params, **_: params.unit.has_dissertation,
        fields__has_placement__include=lambda params, **_: params.unit.has_placement,
        editable=False,
    )



class UnitEdit(Page):
    """
    Edit a unit's details
    """
    header = Header(
        lambda params, **_: params.unit.get_instance_header()
    )
    form = UnitForm.edit(
        h_tag=None,
        instance=lambda params, **_: params.unit,
    )


class UnitCreate(Page):
    """
    Page showing a unit to be created
    """
    header = Header(
        lambda params, **_: Unit.get_model_header_singular()
    )
    form = UnitForm.create(
        h_tag=None,
    )


class UnitList(Page):
    """
    List of all currently active modules.
    """
    header = Header(
        lambda params, **_: Unit.get_model_header()
    )
    list = UnitTable(
        rows=UnitTable.annotate_query_set(Unit.available_objects.all()),
    )


urlpatterns = [
    path('unit/create/', UnitCreate().as_view(), name='unit_create'),
    path('unit/<unit>/create/', UnitTaskCreate().as_view(), name='unit_task_create'),
    path('unit/<unit>/delete/', UnitDelete().as_view(), name='unit_delete'),
    path('unit/<unit>/edit/', UnitEdit().as_view(), name='unit_edit'),
    path('unit/<unit>/<task>/edit/', TaskEdit().as_view(), name='unit_task_edit'),
    path('unit/<unit>/<task>/delete/', TaskDelete().as_view(), name='unit_task_delete'),
    path('unit/<unit>/<task>/', TaskDetail().as_view(), name='unit_task_detail'),
    path('unit/<unit>/', UnitDetail().as_view(), name='unit_detail'),
    path('unit/', UnitList().as_view(), name='unit_list'),
]


def get_menu_units_for_user(user: AbstractUser) -> Dict[str, M]:
    """

    :param user:
    :return:
    """
    units: Dict[str, M] = {}

    for task in user.staff.task_set.all():
        units[task.unit.code] = M(
            open=True,
            view=UnitDetail(pk=task.unit.pk).as_view(),
            display_name=lambda unit, **_: unit.name,
            url=lambda unit, **_: task.unit.get_absolute_url(),
        )

    return units
