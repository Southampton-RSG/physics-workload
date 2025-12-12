from logging import Logger, getLogger

from django.http import HttpResponseRedirect
from iommi import Action, EditColumn, EditTable, Table

from app.models import Assignment, Staff, Task
from app.style import base_style, floating_fields_select2_inline_style
from app.utility import update_all_loads

logger: Logger = getLogger(__name__)


class AssignmentStaffTable(Table):
    """
    Table that appears on Staff pages, for non-staff users.
    """

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


def handle_bulk_approval(table, request, **_):
    table.rows.update(is_provisional=False)
    return HttpResponseRedirect(request.META["HTTP_REFERER"])


def test_func(_):
    if _["form"].instance and hasattr(_["form"].instance, "task"):
        return _["form"].instance.task.assignment_students != Task.AssignmentStudentsChoices.INVALID
    else:
        return True


# row.assignment_students != Task.AssignmentStudentsChoices.INVALID
class AssignmentStaffEditTable(EditTable):
    """
    Table that appears on Staff pages for staff users, with editable assignments.
    """

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
                # students=EditColumn.integer(
                #     model=Task,
                #     model_field_name='students',
                field=dict(
                    include=lambda user, **_: user.is_staff,
                    editable=lambda **_: test_func(_),
                ),
                cell=dict(
                    attrs__style={"width": "6em"},
                    # value=lambda **_: test_func(_),
                    # template=Template("{% if row.task.assignment_students != 'INVALID' %}{{ bound_cell }}{% else %}<td></td>{% endif %}")
                    # template=Template("<td style='width:6em'>{% if row.task.assignment_students != 'INVALID' %}{{ bound_cell }}{% endif %}</td>")
                ),
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
            ),
            delete=EditColumn.delete(
                header__attrs__class={"text-center": True},
                cell__attrs__class={"text-center": True},
                cell__attrs__style={"width": "3em"},
            ),
        )
        rows = lambda staff, **_: Assignment.objects.filter(staff=staff)
        iommi_style = floating_fields_select2_inline_style
        edit_actions = dict(
            save=dict(attrs__class={"btn-primary": False, "btn-success": True}),
            approve_provisional=Action.submit(
                display_name="Approve Provisional",
                attrs__class={"btn-primary": False, "btn-info": True},
                post_handler=handle_bulk_approval,
            ),
        )

        @staticmethod
        def extra__post_save(staff: Staff, **_):
            """
            :param staff:
            :param _:
            :return:
            """
            update_all_loads()


class AssignmentTaskTable(EditTable):
    """
    Table that appears on Task pages, for non-staff users.
    """

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
    """
    Table that appears on Task pages for staff users, with editable assignments.
    """

    class Meta:
        auto = dict(
            model=Assignment,
            exclude=["notes"],
        )
        columns = dict(
            task=EditColumn.hardcoded(
                render_column=False,
                field__include=True,
                field__parsed_data=lambda task, **_: task,
            ),
            load_calc=dict(include=lambda task, **_: task.assignment_students != Task.AssignmentStudentsChoices.INVALID),
            students=dict(
                include=lambda task, **_: task.assignment_students != Task.AssignmentStudentsChoices.INVALID,
                field__include=lambda task, **_: task.assignment_students != Task.AssignmentStudentsChoices.INVALID,
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
        edit_actions = dict(
            save=dict(attrs__class={"btn-primary": False, "btn-success": True}),
            approve_provisional=Action.submit(
                display_name="Approve Provisional",
                attrs__class={"btn-primary": False, "btn-info": True},
                post_handler=handle_bulk_approval,
            ),
        )

        @staticmethod
        def extra__post_save(task: Task, **_):
            """
            :param task:
            :param _:
            :return:
            """
            update_all_loads()
