from iommi import Column, Header, Page, Table

from app.forms.unit import UnitForm
from app.models import Assignment, Task, Unit
from app.pages.components.suffixes import SuffixHistory
from app.tables.task import TaskTable


class UnitHistoryDetail(Page):
    """
    View showing the detail of a unit at a point in time.
    """
    header = Header(
        lambda unit, **_: unit.get_instance_header(),
        children__suffix=SuffixHistory(
            text=lambda staff_history, **_: f" / {staff_history.history_date.date()} "
        )
    )
    tasks = TaskTable(
        h_tag=Header,
        columns=dict(
            unit_code__include=False,
            assignment_set=Column(
                cell=dict(
                    template='app/unit/assignment_set.html',
                    value=lambda row, unit, unit_history, **_: Assignment.history.as_of(
                        unit_history.history_date
                    ).filter(task=row).all(),
                )
            ),
        ),
        query__include=False,
        rows=lambda unit, unit_history, **_: TaskTable.annotate_query_set(
            Task.history.as_of(unit_history.history_date).filter(unit=unit)
        ),
    )
    form = UnitForm(
        title="Details",
        instance=lambda unit, **_: unit,
        fields__name__include=False,
        fields__code__include=False,
        fields__lectures__include=lambda unit, **_: unit.lectures,
        fields__problem_classes__include=lambda unit, **_: unit.problem_classes,
        fields__coursework__include=lambda unit, **_: unit.coursework,
        fields__synoptic_lectures__include=lambda unit, **_: unit.synoptic_lectures,
        fields__exams__include=lambda unit, **_: unit.exams,
        fields__exam_mark_fraction__include=lambda unit, **_: unit.exam_mark_fraction,
        fields__coursework_mark_fraction__include=lambda unit, **_: unit.coursework_mark_fraction,
        fields__has_dissertation__include=lambda unit, **_: unit.has_dissertation,
        fields__has_placement__include=lambda unit, **_: unit.has_placement,
        editable=False,
    )


class UnitHistoryList(Page):
    """
    List of all historical entries for a Unit.
    """
    header = Header(
        lambda unit, **_: unit.get_instance_header(),
        children__suffix=SuffixHistory(),
    )
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
