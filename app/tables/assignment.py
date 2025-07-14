from logging import getLogger, Logger
from typing import List, Dict

from django.db.models import Q, QuerySet, Subquery
from django.test.signals import static_finders_changed
from django.utils.html import format_html

from iommi import Table, EditTable, EditColumn, Action, Form

from app.models import Assignment, Staff, Task, StandardLoad
from app.style import floating_fields_select2_inline_style, base_style


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
            notes__include=False,

            staff=EditColumn.hardcoded(
                render_column=False,
                field__include=lambda user, **_: user.is_staff,
                field__parsed_data=lambda staff, **_: staff,
            ),
            students=dict(
                field__include=lambda user, **_: user.is_staff,
                cell__attrs__style={'width': '6em'},
            ),
            load_calc=dict(
                after='task',
                field__include=False,
                cell=dict(
                    value=lambda row, **_: f"{row.load_calc:.0f}",
                    attrs__class={'align-middle': True},
                ),
            ),
            is_first_time=dict(
                field=dict(
                    include=lambda user, **_: user.is_staff,
                    iommi_style=base_style,
                ),
                cell__attrs__style={'width': '6em'},
                cell__attrs__class={'align-middle': True},
            ),
            is_provisional=dict(
                field=dict(
                    include=lambda user, **_: user.is_staff,
                    iommi_style=base_style,
                ),
                cell__attrs__style={'width': '6em'},
                cell__attrs__class={'align-middle': True},
            ),
            task=dict(
                field=dict(
                    include=lambda user, **_: user.is_staff,
                ),
                cell=dict(
                    value=lambda row, **_: row.task.get_name() if hasattr(row, 'task') else None,
                    url=lambda row, **_: row.task.get_absolute_url() if hasattr(row, 'task') else None,
                ),
            ),
            delete=EditColumn.delete(
                include=lambda user, **_: user.is_staff,
                header__attrs__class={'text-center': True},
                cell__attrs__class={'text-center': True},
                cell__attrs__style={'width': '3em'},
            ),
        )
        rows=lambda staff, **_: Assignment.objects.filter(staff=staff)
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
            for assignment in staff.assignment_set.all():
                assignment.update_load()

            if staff.update_load_assigned():
                logger.info(
                    "Staff has updated load, requiring update to total load target."
                )
                standard_load: StandardLoad = StandardLoad.objects.latest()
                standard_load.update_target_load_per_fte()

