"""

"""
import string
from logging import getLogger

from django.template.loader import render_to_string
from django.urls import path
from django.utils.html import format_html

from iommi import Page, Table, html, Form, EditTable, Column, Field, EditColumn, Header

from app.models import Unit, Task, Assignment, Staff, StandardLoad
from app.forms.task import TaskForm
from app.tables.task import TaskTable


# Set up logging for this file
logger = getLogger(__name__)


class TaskDetail(Page):
    """
    Page for showing task details
    """
    header = Header(
        lambda params, **_: params.task.get_instance_header()
    )

    @staticmethod
    def filter_staff(task):
        staff_allocated = task.assignment_set.filter(is_removed=False).values_list('staff', flat=True)
        print(staff_allocated)
        staff_allowed = Staff.objects.exclude(pk__in=staff_allocated)
        print(staff_allowed)
        return staff_allowed

    list = EditTable(
        auto__model=Assignment,
        auto__exclude=['notes', 'load_calc'],
        columns__task=EditColumn.hardcoded(
            render_column=False,
            field__parsed_data=lambda params, **_: params.task,
        ),
        columns__staff=Column.choice_queryset(
            cell__url=lambda row, **_: row.staff.get_absolute_url() if hasattr(row, 'staff') else '',
            choices=lambda params, **_: TaskDetail.filter_staff(params.task),
        #     choices=lambda params, **_: Staff.objects.filter(
        #         pk__in=params.task.assignment_set.values_list('staff__pk', flat=True)
        #     )
        ),
        columns__delete=EditColumn.delete(),
        rows=lambda params, **_: params.task.assignment_set.filter(is_removed=False).all(),
    )
    br = html.br()
    form = TaskForm(
        title="Details",
        auto__model=Task, instance=lambda params, **_: params.task,
        auto__exclude=['unit', 'is_removed'],
        fields__coursework_fraction__include=lambda params, **_: params.task.coursework_fraction,
        fields__exam_fraction__include=lambda params, **_: params.task.exam_fraction,
        fields__load_function__include=lambda params, **_: params.task.students,
        fields__students__include=lambda params, **_: params.task.students,
        editable=False,
        actions__submit=None,
    )


class TaskEdit(Page):
    """
    Page for editing a task
    """
    header = Header(
        lambda params, **_: params.task.get_instance_header()
    )
    form = TaskForm.edit(
        h_tag=None,
        fields__load_calc_first__include=False,
        fields__load_calc__include=False,
        instance=lambda params, **_: params.task,
        extra__redirect_to='..',
    )


class TaskCreate(Page):
    """
    Page for creating a task
    """
    header = Header(
        lambda params, **_: Task.get_model_header_singular()
    )
    form = TaskForm.create(
        h_tag=None,
        fields__unit__include=False,
        fields__load_calc_first__include=False,
        fields__load_calc__include=False,
        fields__standard_load=Field.non_rendered(
            include=True,
            initial=lambda params, **_: StandardLoad.objects.latest(),
        )
    )


class TaskDelete(Page):
    """
    Page for deleting a task
    """
    header = Header(
        lambda params, **_: params.task.get_instance_header()
    )
    form = TaskForm.delete(
        h_tag=None,
        instance=lambda params, **_: params.task,
    )


class TaskList(Page):
    """
    Page for listing tasks
    """
    header = Header(
        lambda params, **_: Task.get_model_header(),
    )
    list = TaskTable(
        rows=TaskTable.annotate_query_set(Task.available_objects.all()),
    )


urlpatterns = [
    path('task/create/', TaskCreate().as_view(), name='task_create'),
    path('task/<task>/delete/', TaskDelete().as_view(), name='task_delete'),
    path('task/<task>/edit/', TaskEdit().as_view(), name='task_edit'),
    path('task/<task>/', TaskDetail().as_view(), name='task_detail'),
    path('task/', TaskList().as_view(), name='task_list'),
]