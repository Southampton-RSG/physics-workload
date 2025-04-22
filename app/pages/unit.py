"""
Pages for academic units
"""
from typing import Dict
from django.contrib.auth.models import AbstractUser, AnonymousUser
from django.urls import path
from django.utils.html import format_html
from django.template import Template, Context
from django.template.loader import render_to_string

from iommi import Page, Field, Header, Column, Table
from iommi.path import register_path_decoding
from iommi.experimental.main_menu import M

from app.auth import has_access_decoder
from app.forms.task import TaskForm
from app.forms.unit import UnitForm
from app.pages.task import TaskDetail, TaskEdit, TaskDelete
from app.models import Unit, Task, Assignment
from app.tables.task import TaskTable
from app.tables.unit import UnitTable


class UnitTaskCreate(Page):
    """
    Create a task associated with a unit
    """
    header = Header(
        lambda params, **_: params.unit.get_instance_header(suffix="Create Task")
    )
    form = TaskForm.create(
        h_tag=None,
        fields__unit=Field.non_rendered(
            initial=lambda params, **_: params.unit,
        ),
    )


class UnitDetail(Page):
    """
    View a unit and its associated tasks
    """
    header = Header(
        lambda params, **_: params.unit.get_instance_header()
    )
    tasks = TaskTable(
        h_tag=Header,
        columns__unit_code__include=False,
        query__include=False,
        rows=lambda params, **_: TaskTable.annotate_query_set(params.unit.task_set.filter(is_removed=False).all()),
        columns__assignment_set__cell__template='app/unit/assignment_set.html',
    )
    form = UnitForm(
        title="Details",
        instance=lambda params, **_: params.unit,
        fields__name__include=False,
        fields__code__include=False,
        fields__lectures__include=lambda params, **_: params.unit.lectures,
        fields__problem_classes__include=lambda params, **_: params.unit.problem_classes,
        fields__coursework__include=lambda params, **_: params.unit.coursework,
        fields__synoptic_lectures__include=lambda params, **_: params.unit.synoptic_lectures,
        fields__exams__include=lambda params, **_: params.unit.exams,
        fields__exam_mark_fraction__include=lambda params, **_: params.unit.exam_mark_fraction,
        fields__coursework_mark_fraction__include=lambda params, **_: params.unit.coursework_mark_fraction,
        fields__has_dissertation__include=lambda params, **_: params.unit.has_dissertation,
        fields__has_placement__include=lambda params, **_: params.unit.has_placement,
        editable=False,
    )


class UnitDelete(Page):
    """
    View a unit and its associated tasks
    """
    header = Header(
        lambda params, **_: params.unit.get_instance_header()
    )
    form = UnitForm.delete(
        h_tag=None,
        instance=lambda params, **_: params.unit,
         fields__name__include=False,
        fields__code__include=False,
        fields__lectures__include=lambda params, **_: params.unit.lectures,
        fields__problem_classes__include=lambda params, **_: params.unit.problem_classes,
        fields__coursework__include=lambda params, **_: params.unit.coursework,
        fields__synoptic_lectures__include=lambda params, **_: params.unit.synoptic_lectures,
        fields__exams__include=lambda params, **_: params.unit.exams,
        fields__exam_mark_fraction__include=lambda params, **_: params.unit.exam_mark_fraction,
        fields__coursework_mark_fraction__include=lambda params, **_: params.unit.coursework_mark_fraction,
        fields__has_dissertation__include=lambda params, **_: params.unit.has_dissertation,
        fields__has_placement__include=lambda params, **_: params.unit.has_placement,
        editable=False,
    )


class UnitEdit(Page):
    """
    Edit a unit's details
    """
    header = Header(
        lambda params, **_: params.unit.get_instance_header()
    )
    form = UnitForm.edit(
        h_tag=None,
        instance=lambda params, **_: params.unit,
    )


class UnitCreate(Page):
    """
    Page showing a unit to be created
    """
    header = Header(
        lambda params, **_: Unit.get_model_header_singular()
    )
    form = UnitForm.create(
        h_tag=None,
    )


class UnitList(Page):
    """
    List of all currently active modules.
    """
    header = Header(
        lambda params, **_: Unit.get_model_header()
    )
    list = UnitTable(
        rows=UnitTable.annotate_query_set(Unit.available_objects.all()),
    )


class UnitHistoryDetail(Page):
    """
    View showing the detail of a unit at a point in time.
    """
    header = Header(
        lambda params, **_: params.unit.get_instance_header(suffix=f"{params.unit_history.history_date.date()}")
    )
    # Can't use assignment_set, so need a custom table for history that pulls the assignments itself.
    # tasks = TaskTable(
    #     h_tag=Header,
    #     columns=dict(
    #         unit_code__include=False,
    #         assignment_set=Column(
    #             cell=dict(
    #                 template='app/unit/assignment_set.html',
    #                 value=lambda row, params, **_: Assignment.history.as_of(
    #                     params.unit_history.history_date
    #                 ).filter(task=row).all(),
    #             )
    #         ),
    #     ),
    #     query__include=False,
    #     rows=lambda params, **_: TaskTable.annotate_query_set(
    #         Task.history.as_of(params.unit_history.history_date).filter(unit=params.unit, is_removed=False)
    #     ),
    # )
    form = UnitForm(
        title="Details",
        instance=lambda params, **_: params.unit,
        fields__name__include=False,
        fields__code__include=False,
        fields__lectures__include=lambda params, **_: params.unit.lectures,
        fields__problem_classes__include=lambda params, **_: params.unit.problem_classes,
        fields__coursework__include=lambda params, **_: params.unit.coursework,
        fields__synoptic_lectures__include=lambda params, **_: params.unit.synoptic_lectures,
        fields__exams__include=lambda params, **_: params.unit.exams,
        fields__exam_mark_fraction__include=lambda params, **_: params.unit.exam_mark_fraction,
        fields__coursework_mark_fraction__include=lambda params, **_: params.unit.coursework_mark_fraction,
        fields__has_dissertation__include=lambda params, **_: params.unit.has_dissertation,
        fields__has_placement__include=lambda params, **_: params.unit.has_placement,
        editable=False,
    )


class UnitHistoryList(Page):
    """
    List of all historical entries for a Unit.
    """
    header = Header(lambda params, **_: params.unit.get_instance_header(suffix="History"))
    list = Table(
        auto__model=Unit,
        h_tag=None,
        auto__include=['students'],
        columns=dict(
            history_date=Column(
                cell=dict(
                    url=lambda params, row, **_: f"{row.history_id}/",
                    value=lambda params, row, **_: row.history_date.date(),
                ),
            ),
            history_id = Column(
                render_column=False,
            ),
        ),
        rows=lambda params, **_: params.unit.history.all(),
    )


# Decodes "<unit>" in paths into `params.unit`
register_path_decoding(
    unit=has_access_decoder(Unit, "You must be assigned to a Unit to view it"),
)
register_path_decoding(
    unit_history=lambda string, **_: Unit.history.get(history_id=int(string)),
)

# Added to the main menu
unit_submenu: M = M(
    icon=Unit.icon,
    include=lambda request, **_: request.user.is_authenticated,
    view=UnitList,

    items=dict(
        create=M(
            icon="plus",
            include=lambda request, **_: request.user.is_staff,
            view=UnitCreate,
        ),
        detail=M(
            display_name=lambda unit, **_: unit.code,
            open=True,
            params={'unit'},
            path='<unit>/',
            url=lambda unit, **_: f"/{Unit.url_root}/{unit.pk}/",
            view=UnitDetail,

            items=dict(
                edit=M(
                    icon='pencil',
                    view=UnitEdit,
                    include=lambda request, **_: request.user.is_staff,
                ),
                delete=M(
                    icon='trash',
                    view=UnitDelete,
                    include=lambda request, **_: request.user.is_staff,
                ),
                # history=M(
                #     icon='clock-rotate-left',
                #     view=UnitHistoryList,
                #     items=dict(
                #         detail=M(
                #             display_name=lambda unit_history, **_: unit_history.history_date.date(),
                #             params={'unit_history'},
                #             path='<unit_history>/',
                #             view=UnitHistoryDetail,
                #         )
                #     )
                # ),
                task_detail=M(
                    display_name=lambda task, **_: task.name,
                    icon=Task.icon,
                    open=True,
                    params={'unit', 'task'},
                    path='<task>/',
                    url=lambda task, **_: f"/{Unit.url_root}/{task.unit.pk}/{task.pk}/",
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
                    )
                ),
                create = M(
                    display_name="Create Task",
                    icon='plus',
                    view=UnitTaskCreate,
                    include=lambda request, **_: request.user.is_staff,
                ),
            ),
        )
    )
)
