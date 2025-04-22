"""

"""
from logging import getLogger
from typing import List

from django.urls import path
from django.db.models import QuerySet

from iommi import Page, html, EditTable, Column, Field, EditColumn, Header, register_search_fields
from iommi.path import register_path_decoding
from iommi.experimental.main_menu import M

from app.auth import has_access_decoder
from app.models import Task, Assignment, Staff, StandardLoad
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
        staff_allocated: List[Staff] = task.assignment_set.filter(is_removed=False).values_list('staff', flat=True)
        staff_allowed: QuerySet[Staff] = Staff.objects.exclude(pk__in=staff_allocated)
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


# Register tasks to be searched using the "name" field.
register_search_fields(
    model=Task, search_fields=['name'], allow_non_unique=True
)
# Decode <task> in paths so a LoadFunction object is in the view parameters.
register_path_decoding(
    task=has_access_decoder(Task, "You must be assigned to a Task to view it."),
)

# This is imported into the main menu tree.
task_submenu: M = M(
    display_name=Task._meta.verbose_name_plural,
    icon=Task.icon,
    include=lambda request, **_: request.user.is_authenticated,
    view=TaskList,

    items=dict(
        create=M(
            icon="plus",
            view=TaskCreate,
            include=lambda request, **_: request.user.is_staff,
        ),
        detail=M(
            display_name=lambda task, **_: task.name,
            params={'task'},
            path='<task>/',
            url=lambda task, **_: f"{Task.url_root}/{task.pk}/",
            view=TaskDetail,

            items=dict(
                edit=M(
                    icon='pencil',
                    view=TaskEdit,
                    include=lambda request, **_: request.user.is_staff,
                ),
                delete=M(
                    icon='trash',
                    view=TaskDelete,
                    include=lambda request, **_: request.user.is_staff,
                ),
                # history=M(
                #     icon='clock-rotate-left',
                #     view=TaskHistory,
                # )
            )
        )
    )
)
