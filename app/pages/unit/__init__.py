"""
Pages for academic units
"""
from django.utils.html import format_html
from iommi import Header, Page, html

from app.forms.unit import UnitForm
from app.models import Task, Unit
from app.pages.components.suffixes import SuffixCreate, SuffixDelete, SuffixEdit
from app.tables.task import TaskTable
from app.tables.unit import UnitTable


class UnitDetail(Page):
    """
    View a unit and its associated tasks
    """
    header = Header(
        lambda unit, **_: unit.get_instance_header()
    )
    tasks = TaskTable(
        columns=dict(
            owner__include=False,
            assignment_set__cell__template='app/unit/assignment_set.html',
        ),
        h_tag=Header,
        query__include=False,
        rows=lambda unit, **_: Task.objects.filter(unit=unit).all(),
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


class UnitDelete(Page):
    """
    View a unit and its associated tasks
    """
    header = Header(
        lambda unit, **_: unit.get_instance_header(),
        children__suffix=SuffixDelete(),
    )
    form = UnitForm.delete(
        h_tag=None,
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


class UnitEdit(Page):
    """
    Edit a unit's details
    """
    header = Header(
        lambda unit, **_: unit.get_instance_header(),
        children__suffix=SuffixEdit(),
    )
    form = UnitForm.edit(
        h_tag=None,
        instance=lambda unit, **_: unit,
    )


class UnitCreate(Page):
    """
    Page showing a unit to be created
    """
    header = Header(
        lambda params, **_: Unit.get_model_header_singular(),
        children__suffix=SuffixCreate(),
    )
    text = html.p(
        format_html("Units should be created on here and on <a href='https://soton.worktribe.com/'>WorkTribe</a>."),
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
        rows=UnitTable.annotate_query_set(Unit.objects.all()),
    )
