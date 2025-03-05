"""

"""
import string
from logging import getLogger

from django.urls import path
from django.utils.html import format_html

from iommi import Page, Table, html, Form, EditTable, Column, Field, EditColumn
from iommi.path import register_path_decoding
from iommi import register_search_fields

from app.models import Unit, Task, Assignment, Staff
from app.pages import BasePage, HeaderInstanceDelete, HeaderInstanceEdit, HeaderInstanceDetail, HeaderList, ColumnModify, HeaderInstanceCreate
from app.forms.task import TaskForm
from app.tables.task import TaskTable


# Set up logging for this file
logger = getLogger(__name__)

register_path_decoding(task=lambda string, **_: Task.objects.get(pk=int(string)))


class TaskDetail(BasePage):
    """
    Page for showing task details
    """
    header = HeaderInstanceDetail(
        lambda params, **_: format_html(
            f"{params.task.get_instance_header()}"
        )
    )

    @staticmethod
    def filter_staff(task):
        staff_allocated = task.assignment_set.values_list('staff', flat=True)
        print(staff_allocated)
        staff_allowed = Staff.objects.exclude(pk__in=staff_allocated)
        print(staff_allowed)
        return staff_allowed

    list = EditTable(
        auto__model=Assignment,
        auto__exclude=['notes'],
        columns__staff__field__include=True,
        columns__is_first_time__field__include=True,
        columns__is_provisional__field__include=True,
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
        rows=lambda params, **_: params.task.assignment_set.all(),
    )
    br = html.br()
    form = TaskForm(
        title="Details",
        auto__model=Task, instance=lambda params, **_: params.task,
        auto__exclude=['unit', 'is_active'],
        fields__coursework_fraction__include=lambda params, **_: params.task.coursework_fraction,
        fields__exam_fraction__include=lambda params, **_: params.task.exam_fraction,
        fields__load_function__include=lambda params, **_: params.task.students,
        fields__students__include=lambda params, **_: params.task.students,
        editable=False,
    )


class TaskEdit(BasePage):
    """
    Page for editing a task
    """
    header = HeaderInstanceEdit(
        lambda params, **_: params.task.get_instance_header()
    )
    form = TaskForm.edit(
        h_tag=None,
        fields__load_calc_first__include=False,
        fields__load_calc__include=False,
        instance=lambda params, **_: params.task,
        extra__redirect_to='..',
    )


class TaskCreate(BasePage):
    """
    Page for creating a task
    """
    header = HeaderInstanceCreate(
        lambda params, **_: Task.get_model_header()
    )
    form = TaskForm.create(
        h_tag=None,
        fields__unit__include=False,
        fields__load_calc_first__include=False,
        fields__load_calc__include=False,
    )


class TaskDelete(BasePage):
    """
    Page for deleting a task
    """
    header = HeaderInstanceDelete(
        lambda params, **_: params.task.get_instance_header()
    )
    form = TaskForm.delete(
        h_tag=None,
        instance=lambda params, **_: params.task,
    )


class TaskList(BasePage):
    """
    Page for listing tasks
    """
    header = HeaderList(
        lambda params, **_: Task.get_model_header(),
    )
    list = TaskTable(
        rows=TaskTable.annotate_query_set(Task.objects.all()),
    )


urlpatterns = [
    path('task/create/', TaskCreate().as_view(), name='task_create'),
    path('task/<task>/delete/', TaskDelete().as_view(), name='task_delete'),
    path('task/<task>/edit/', TaskEdit().as_view(), name='task_edit'),
    path('task/<task>/', TaskDetail().as_view(), name='task_detail'),
    path('task/', TaskList().as_view(), name='task_list'),
]