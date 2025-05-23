from logging import getLogger, Logger
from typing import List, Dict

from django.db.models import Q, QuerySet, Subquery
from django.test.signals import static_finders_changed
from django.utils.html import format_html

from iommi import Table, EditTable, EditColumn, Action, Form

from app.models import Assignment, Staff, Task, StandardLoad
from app.style import floating_fields_select2_inline_style


logger: Logger = getLogger(__name__)


class AssignmentTable(Table):
    """

    """
    class Meta:
        auto__model = Assignment
        columns = dict(
            is_provisional__attrs__class = {'text-right': False, 'text-center': True},
            is_first_time__attrs__class = {'text-right': False, 'text-center': True},
        )


class AssignmentStaffTable(EditTable):
    """

    """
    class Meta:
        auto__model=Assignment
        columns=dict(
            is_removed__include=False,
            notes__include=False,

            staff=EditColumn.hardcoded(
                render_column=False,
                field__include=lambda user, **_: user.is_staff,
                field__parsed_data=lambda params, **_: params.staff,
            ),
            students=dict(
                field__include=lambda user, **_: user.is_staff,
                cell__attrs__style={'width': '6em'},
            ),
            load_calc=dict(
                after='task',
                field__include=False,
                cell__value=lambda row, **_: f"{row.load_calc:.0f}",
            ),
            is_first_time=dict(
                field__include=lambda user, **_: user.is_staff,
                cell__attrs__style={'width': '6em'},
            ),
            is_provisional=dict(
                field__include=lambda user, **_: user.is_staff,
                cell__attrs__style={'width': '6em'},
            ),
            task=dict(
                field__choices=lambda staff, instance, **_: AssignmentStaffTable.task_choices(staff, instance, **_),
            ),
            delete=EditColumn.delete(
                include=lambda user, **_: user.is_staff,
                display_name=format_html("<i class='fa-solid fa-trash'></i>"),
                header__attrs__class={'text-center': True},
                cell__attrs__class={'text-center': True},
                cell__attrs__style={'width': '3em'},
            ),
        )
        rows=lambda params, **_: Assignment.available_objects.filter(staff=params.staff)
        iommi_style=floating_fields_select2_inline_style
        edit_actions=dict(
            save__include=lambda user, **_: user.is_staff,
            add_row=Action.button(
                include=lambda user, **_: user.is_staff,
                display_name="New assignment",
                attrs__onclick='iommi_add_row(this); return false',
            )
        )

        @staticmethod
        def extra__post_save(
               staff: Staff, **_
        ):
            """

            :param staff:
            :param _:
            :return:
            """
            needs_update: bool = False

            for assignment in staff.assignment_set.all():
                needs_update += assignment.update_load()

            if needs_update:
                standard_load: StandardLoad = StandardLoad.objects.latest()
                standard_load.update_target_load_per_fte()

    @staticmethod
    def task_choices(staff: Staff, instance: Assignment, **_):
        tasks_current = staff.assignment_set.values_list('task_id', flat=True)
        tasks_allowed = Task.objects.none() | Task.available_objects.exclude(id__in=tasks_current)
        return tasks_allowed.order_by('name', 'unit', 'academic_group')
