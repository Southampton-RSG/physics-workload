"""

"""
from logging import getLogger
from typing import List

from django.db.models import QuerySet

from iommi import Page, html, EditTable, Column, Field, EditColumn, Header, register_search_fields

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
        auto__exclude=[
            'is_removed', 'academic_group', 'unit', 'name',
        ],
        instance=lambda params, **_: params.task,
        fields=dict(
            name__include=False,
            load_calc=dict(
                group="Calculated Load",
            ),
            load_calc_first=dict(
                include=lambda params, **_: params.task.load_calc_first and params.task.load_calc_first != params.task.load_calc,
                group="Calculated Load",
            ),
            load_coordinator=dict(
                include=lambda params, **_: params.task.unit,
                group="Calculation Details",
                after='load_calc_first',
            ),
            load_fixed_first=dict(
                include=lambda params, **_: params.task.load_fixed_first
            ),
            coursework_fraction=dict(
                include=lambda params, **_: params.task.load_coordinator,
                group="Calculation Details",
                after='load_coordinator',
            ),
            exam_fraction=dict(
                include=lambda params, **_: params.task.load_coordinator,
                group="Calculation Details",
            ),
            load_function__include=lambda params, **_: params.task.load_function,
            students__include=lambda params, **_: params.task.students,
        ),
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
        fields=dict(
            load_coordinator__include=lambda params, **_: params.task.unit,
            load_calc__include=False,
            load_calc_first__include=False,
        ),
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
        fields=dict(
            unit__include=False,
            load_calc_first__include=False,
            load_calc__include=False,
            load_fixed_first__include=True,
            load_coordinator__include=False,
            standard_load=Field.non_rendered(
                include=True,
                initial=lambda params, **_: StandardLoad.objects.latest(),
            )
        ),
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
        fields=dict(
            load_calc_first__include=lambda params, **_: params.task.load_calc_first,
            load_fixed_first=dict(
                include=lambda params, **_: params.task.load_fixed_first
            ),
        ),
    )


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