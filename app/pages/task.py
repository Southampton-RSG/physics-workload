"""
Pages relating to showing and managing tasks.

Handle the general 'non-unit' task creation, and all task editing and deletion.
"""

from logging import Logger, getLogger
from typing import List

from django.db.models import QuerySet
from iommi import Header, Page, html, register_search_fields

from app.forms.assignment import AssignmentTaskUniqueForm
from app.forms.info import InfoForm
from app.forms.task import TaskCreateForm, TaskDetailForm, TaskEditForm, TaskFullTimeCreateForm
from app.models import Info, Staff, Task
from app.pages.components.suffixes import SuffixCreate, SuffixCreateFullTime, SuffixDelete, SuffixEdit
from app.tables.assignment import AssignmentTaskEditTable, AssignmentTaskTable
from app.tables.task import TaskTable

# Set up logging for this file
logger: Logger = getLogger(__name__)


class TaskDetail(Page):
    """
    Page for showing task details
    """

    header = Header(
        lambda task, **_: task.get_instance_header(),
    )

    @staticmethod
    def filter_staff(task):
        staff_allocated: List[Staff] = task.assignment_set.values_list("staff", flat=True)
        staff_allowed: QuerySet[Staff] = Staff.objects.exclude(pk__in=staff_allocated)

        if task.unit and task.unit.academic_group:
            staff_allowed = staff_allowed.filter(academic_group=task.unit.academic_group)

        elif task.academic_group:
            staff_allowed = staff_allowed.filter(academic_group=task.academic_group)

        return staff_allowed

    assignments = AssignmentTaskTable(
        include=lambda user, task, **_: not task.is_unique and not user.is_staff,
    )
    assignments_editable = AssignmentTaskEditTable(
        include=lambda user, task, **_: not task.is_unique and user.is_staff,
    )
    assignment = AssignmentTaskUniqueForm(
        include=lambda user, task, **_: task.assignment_set.count() and task.is_unique and not user.is_staff,
        instance=lambda task, **_: task.assignment_set.first() if task.assignment_set.count() else None,
    )
    assignment_create = AssignmentTaskUniqueForm.create_or_edit(
        include=lambda user, task, **_: task.is_unique and user.is_staff,
        instance=lambda task, **_: task.assignment_set.first() if task.assignment_set.count() else None,
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
        lambda task, **_: task.get_instance_header(),
        children__suffix=SuffixEdit(),
    )
    form = TaskEditForm.edit()


class TaskCreate(Page):
    """
    Page for creating a task
    """

    header = Header(
        lambda params, **_: Task.get_model_header_singular(),
        children__suffix=SuffixCreate(),
    )
    form = TaskCreateForm.create(extra__redirect_to="..")


class TaskDelete(Page):
    """
    Page for deleting a task
    """

    header = Header(
        lambda task, **_: task.get_instance_header(),
        children__suffix=SuffixDelete(),
    )
    form = TaskDetailForm.delete()


class TaskList(Page):
    """
    Page for listing tasks
    """

    header = Header(
        lambda params, **_: Task.get_model_header(),
    )
    info = InfoForm(
        instance=lambda **_: Info.objects.get(page="task"),
    )
    list = TaskTable(
        h_tag=None,
        rows=TaskTable.annotate_query_set(Task.objects.all()),
    )


class TaskFullTimeCreate(Page):
    """
    Page for creating a task that's full time
    """

    header = Header(
        lambda params, **_: Task.get_model_header_singular(),
        children__suffix=SuffixCreateFullTime(),
    )
    form = TaskFullTimeCreateForm.create()


# Register tasks to be searched using the "name" field.
register_search_fields(model=Task, search_fields=["name"], allow_non_unique=True)
