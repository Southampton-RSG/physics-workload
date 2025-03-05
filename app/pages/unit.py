"""

"""
from django.db.models import Count, Sum, Q, Case, When, Subquery, OuterRef
from django.urls import path
from django.utils.html import format_html
from django.template.loader import render_to_string

from iommi import Table, html, Form, Column, Field, LAST, Header, Asset, Action
from iommi.path import register_path_decoding

from app.forms.task import TaskForm
from app.forms.unit import UnitForm
from app.pages import BasePage, HeaderList, HeaderInstanceDetail, HeaderInstanceEdit, HeaderInstanceCreate, \
    HeaderInstanceDelete, ColumnModify
from app.models import Unit, Task, Assignment
from app.style import floating_fields_style
from app.tables.task import TaskTable
from app.tables.unit import UnitTable


register_path_decoding(unit=lambda string, **_: Unit.objects.get(code=string))


class UnitTaskCreate(BasePage):
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


class UnitDetail(BasePage):
    """
    View a unit and its associated tasks
    """
    header = HeaderInstanceDetail(
        lambda params, **_: params.unit.get_instance_header()
    )
    tasks = TaskTable(
        h_tag=HeaderList,
        columns__unit_code__include=False,
        query__include=False,
        rows=lambda params, **_: TaskTable.annotate_query_set(params.unit.task_set.all()),
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


class UnitEdit(BasePage):
    """
    Edit a unit's details
    """
    header = HeaderInstanceEdit(
        lambda params, **_: format_html(
            f"{params.unit.get_instance_header()}"
        )
    )
    form = UnitForm.edit(
        h_tag=None,
        instance=lambda params, **_: params.unit,
    )


class UnitCreate(BasePage):
    """
    Page showing a unit to be created
    """
    header = HeaderInstanceCreate(
        lambda params, **_: format_html(
            Unit.get_model_header()
        ),
    )
    form = UnitForm.create(
        h_tag=None,
    )


class UnitList(BasePage):
    """
    List of all currently active modules.
    """
    header = HeaderList(
        lambda params, **_: Unit.get_model_header()
    )
    list = UnitTable(
        rows=UnitTable.annotate_query_set(Unit.objects.all()),
    )


urlpatterns = [
    path('unit/create/', UnitCreate().as_view(), name='unit_create'),
    path('unit/<unit>/create/', UnitTaskCreate().as_view(), name='unit_task_create'),
    path('unit/<unit>/edit/', UnitEdit().as_view(), name='unit_edit'),
    path('unit/<unit>/', UnitDetail().as_view(), name='unit_detail'),
    path('unit/', UnitList().as_view(), name='unit_list'),
]