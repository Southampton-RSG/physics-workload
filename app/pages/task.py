"""

"""
from logging import getLogger
from typing import List

from django.db.models import QuerySet

from iommi import Page, html, EditTable, Column, EditColumn, Header, register_search_fields, Form

from app.models import Task, Assignment, Staff
from app.forms.task import TaskDetailForm, TaskEditForm, TaskCreateForm
from app.tables.task import TaskTable


# Set up logging for this file
logger = getLogger(__name__)


class TaskDetail(Page):
    """
    Page for showing task details
    """
    header = Header(
        lambda params, **_: params.task.get_instance_header(),
    )

    @staticmethod
    def filter_staff(task):
        staff_allocated: List[Staff] = task.assignment_set.filter(is_removed=False).values_list('staff', flat=True)
        staff_allowed: QuerySet[Staff] = Staff.available_objects.exclude(pk__in=staff_allocated)

        print(staff_allowed)

        if task.unit and task.unit.academic_group:
            staff_allowed = staff_allowed.filter(academic_group=task.unit.academic_group)

        elif task.academic_group:
            staff_allowed = staff_allowed.filter(academic_group=task.academic_group)

        return staff_allowed

    list = EditTable(
        auto__model=Assignment,
        auto__exclude=['notes', 'load_calc', 'is_removed'],
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
    form = TaskDetailForm()
    text = html.span(
        children=dict(
            header=Header("Description"),
            description=html.p(lambda task, **_: task.description),
        )
    )


class TaskEdit(Page):
    """
    Page for editing a task
    """
    header = Header(
        lambda params, **_: params.task.get_instance_header()
    )
    form = TaskEditForm.edit()


class TaskCreate(Page):
    """
    Page for creating a task
    """
    header = Header(
        lambda params, **_: Task.get_model_header_singular()
    )
    form = TaskCreateForm.create()


class TaskDelete(Page):
    """
    Page for deleting a task
    """
    header = Header(
        lambda params, **_: params.task.get_instance_header()
    )
    form = TaskDetailForm.delete()


class TaskList(Page):
    """
    Page for listing tasks
    """
    header = Header(
        lambda params, **_: Task.get_model_header(),
    )
    list = TaskTable(
        rows=TaskTable.annotate_query_set(
            Task.available_objects.all()
        ),
    )


# Register tasks to be searched using the "name" field.
register_search_fields(
    model=Task, search_fields=['name'], allow_non_unique=True
)