from logging import Logger, getLogger

from iommi import EditColumn, EditTable, Table

from app.models import Assignment, Staff, Task
from app.style import base_style, floating_fields_select2_inline_style
from app.utility import update_all_loads

logger: Logger = getLogger(__name__)


class AssignmentTable(Table):
    """ """

    class Meta:
        auto__model = Assignment
        columns = dict(
            is_provisional__attrs__class={"text-right": False, "text-center": True},
            is_first_time__attrs__class={"text-right": False, "text-center": True},
        )


class AssignmentStaffTable(Table):
    """ """

    class Meta:
        auto = dict(
            model=Assignment,
            exclude=[
                "notes",
                "staff",
            ],
        )
        columns = dict(
            students=dict(
                cell__attrs__style={"width": "6em"},
            ),
            load_calc=dict(
                after="task",
                cell__attrs__class={"align-middle": True},
            ),
            is_first_time=dict(
                iommi_style=base_style,
                cell__attrs__style={"width": "6em"},
                cell__attrs__class={"align-middle": True},
            ),
            is_provisional=dict(
                iommi_style=base_style,
                cell__attrs__style={"width": "6em"},
                cell__attrs__class={"align-middle": True},
            ),
            task=dict(
                cell=dict(
                    value=lambda row, **_: row.task.get_name(),
                    url=lambda row, **_: row.task.get_absolute_url(),
                ),
            ),
        )
        rows = lambda staff, **_: Assignment.objects.filter(staff=staff)
        iommi_style = floating_fields_select2_inline_style
        include = lambda user, **_: not user.is_staff


class AssignmentStaffEditTable(EditTable):
    """ """

    class Meta:
        auto = dict(
            model=Assignment,
            exclude=["notes"],
        )
        columns = dict(
            notes__include=False,
            staff=EditColumn.hardcoded(
                render_column=False,
                field=dict(
                    include=True,
                    parsed_data=lambda staff, **_: staff,
                ),
            ),
            students=dict(
                field__include=lambda user, **_: user.is_staff,
                cell__attrs__style={"width": "6em"},
            ),
            load_calc=dict(
                after="task",
                field__include=False,
                cell__attrs__class={"align-middle": True},
            ),
            is_first_time=dict(
                field=dict(
                    include=True,
                    iommi_style=base_style,
                ),
                cell__attrs__style={"width": "6em"},
                cell__attrs__class={"align-middle": True},
            ),
            is_provisional=dict(
                field=dict(
                    include=True,
                    iommi_style=base_style,
                ),
                cell__attrs__style={"width": "6em"},
                cell__attrs__class={"align-middle": True},
            ),
            task=dict(
                field__include=True,
                cell=dict(
                    value=lambda row, **_: row.task.get_name() if hasattr(row, "task") else None,
                    url=lambda row, **_: row.task.get_absolute_url() if hasattr(row, "task") else None,
                ),
            ),
            delete=EditColumn.delete(
                header__attrs__class={"text-center": True},
                cell__attrs__class={"text-center": True},
                cell__attrs__style={"width": "3em"},
            ),
        )
        rows = lambda staff, **_: Assignment.objects.filter(staff=staff)
        iommi_style = floating_fields_select2_inline_style
        edit_actions = dict(save=dict(attrs__class={"btn-primary": False, "btn-success": True}))
        include = lambda user, **_: user.is_staff

        @staticmethod
        def extra__post_save(staff: Staff, **_):
            """
            :param staff:
            :param _:
            :return:
            """
            update_all_loads()


class AssignmentTaskTable(EditTable):
    """ """

    class Meta:
        auto = dict(
            model=Assignment,
            exclude=["load_calc", "notes"],
        )
        columns = dict(
            students=dict(
                cell__attrs__style={"width": "6em"},
            ),
            is_first_time=dict(
                iommi_style=base_style,
                cell__attrs__style={"width": "6em"},
                cell__attrs__class={"align-middle": True},
            ),
            is_provisional=dict(
                iommi_style=base_style,
                cell__attrs__style={"width": "6em"},
                cell__attrs__class={"align-middle": True},
            ),
            staff=dict(
                include=True,
                cell=dict(
                    value=lambda row, **_: row.staff.name,
                ),
            ),
        )
        rows = lambda task, **_: Assignment.objects.filter(task=task)
        iommi_style = floating_fields_select2_inline_style


class AssignmentTaskEditTable(EditTable):
    """ """

    class Meta:
        auto = dict(
            model=Assignment,
            exclude=["load_calc", "notes"],
        )
        columns = dict(
            task=EditColumn.hardcoded(
                render_column=False,
                field__include=True,
                field__parsed_data=lambda task, **_: task,
            ),
            students=dict(
                field__include=True,
                cell__attrs__style={"width": "6em"},
            ),
            is_first_time=dict(
                field=dict(
                    include=True,
                    iommi_style=base_style,
                ),
                cell__attrs__style={"width": "6em"},
                cell__attrs__class={"align-middle": True},
            ),
            is_provisional=dict(
                field=dict(
                    include=True,
                    iommi_style=base_style,
                ),
                cell__attrs__style={"width": "6em"},
                cell__attrs__class={"align-middle": True},
            ),
            staff=dict(
                field__include=True,
                cell=dict(
                    value=lambda row, **_: row.staff if hasattr(row, "staff") else None,
                    url=lambda row, **_: row.staff.get_absolute_url() if hasattr(row, "staff") else None,
                ),
            ),
            delete=EditColumn.delete(
                include=lambda user, **_: user.is_staff,
                header__attrs__class={"text-center": True},
                cell__attrs__class={"text-center": True},
                cell__attrs__style={"width": "3em"},
            ),
        )
        rows = lambda task, **_: Assignment.objects.filter(task=task)
        iommi_style = floating_fields_select2_inline_style
        edit_actions = dict(save=dict(attrs__class={"btn-primary": False, "btn-success": True}))

        @staticmethod
        def extra__post_save(task: Task, **_):
            """
            :param task:
            :param _:
            :return:
            """
            update_all_loads()
