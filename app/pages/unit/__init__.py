"""
Pages for academic units
"""
from iommi import Page, Header

from app.forms.unit import UnitForm
from app.models import Unit
from app.tables.task import TaskTable
from app.tables.unit import UnitTable


class UnitDetail(Page):
    """
    View a unit and its associated tasks
    """
    header = Header(
        lambda params, **_: params.unit.get_instance_header()
    )
    tasks = TaskTable(
        columns=dict(
            unit_code__include=False,
            academic_group__include=False,
            assignment_set__cell__template='app/unit/assignment_set.html',
        ),
        h_tag=Header,
        query__include=False,
        rows=lambda params, **_: TaskTable.annotate_query_set(
            params.unit.task_set.filter(is_removed=False).all()
        ),
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


# class UnitHistoryDetail(Page):
#     """
#     View showing the detail of a unit at a point in time.
#     """
#     header = Header(
#         lambda params, **_: params.unit.get_instance_header()
#     )
#     # Can't use assignment_set, so need a custom table for history that pulls the assignments itself.
#     # tasks = TaskTable(
#     #     h_tag=Header,
#     #     columns=dict(
#     #         unit_code__include=False,
#     #         assignment_set=Column(
#     #             cell=dict(
#     #                 template='app/unit/assignment_set.html',
#     #                 value=lambda row, params, **_: Assignment.history.as_of(
#     #                     params.unit_history.history_date
#     #                 ).filter(task=row).all(),
#     #             )
#     #         ),
#     #     ),
#     #     query__include=False,
#     #     rows=lambda params, **_: TaskTable.annotate_query_set(
#     #         Task.history.as_of(params.unit_history.history_date).filter(unit=params.unit, is_removed=False)
#     #     ),
#     # )
#     form = UnitForm(
#         title="Details",
#         instance=lambda params, **_: params.unit,
#         fields__name__include=False,
#         fields__code__include=False,
#         fields__lectures__include=lambda params, **_: params.unit.lectures,
#         fields__problem_classes__include=lambda params, **_: params.unit.problem_classes,
#         fields__coursework__include=lambda params, **_: params.unit.coursework,
#         fields__synoptic_lectures__include=lambda params, **_: params.unit.synoptic_lectures,
#         fields__exams__include=lambda params, **_: params.unit.exams,
#         fields__exam_mark_fraction__include=lambda params, **_: params.unit.exam_mark_fraction,
#         fields__coursework_mark_fraction__include=lambda params, **_: params.unit.coursework_mark_fraction,
#         fields__has_dissertation__include=lambda params, **_: params.unit.has_dissertation,
#         fields__has_placement__include=lambda params, **_: params.unit.has_placement,
#         editable=False,
#     )
#`
#
# class UnitHistoryList(Page):
#     """
#     List of all historical entries for a Unit.
#     """
#     header = Header(lambda params, **_: params.unit.get_instance_header(suffix="History"))
#     list = Table(
#         auto__model=Unit,
#         h_tag=None,
#         auto__include=['students'],
#         columns=dict(
#             history_date=Column(
#                 cell=dict(
#                     url=lambda params, row, **_: f"{row.history_id}/",
#                     value=lambda params, row, **_: row.history_date.date(),
#                 ),
#             ),
#             history_id = Column(
#                 render_column=False,
#             ),
#         ),
#         rows=lambda params, **_: params.unit.history.all(),
#     )


