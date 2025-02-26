"""

"""
from django.urls import path
from django.utils.html import format_html
from django.template import Template

from iommi import Page, Table, html, Form, EditTable, Column
from iommi.path import register_path_decoding
from iommi import register_search_fields
from iommi.views import crud_views

from app.pages import BasePage
from app.models import Unit, Task


register_path_decoding(unit=lambda string, **_: Unit.objects.get(code=string))
# register_search_fields(model=Task, search_fields=['name'], allow_non_unique=True)


class EditTableNoAdd(EditTable):
    class Meta:
        edit_actions__add_row = None


class UnitDetail(BasePage):
    """

    """
    pass


class UnitEdit(BasePage):
    """

    """
    title = html.h1(lambda params, **_: f"{params.unit}")
    instance = Form(
        auto__model=Unit,
        instance=lambda params, **_: params.unit,
        fields__name__group="row_1",
        fields__code__group="row_1",
        fields__academic_group__group="row_1",
        fields__has_dissertation__group='row_2',
        fields__has_placement__group='row_2',
        fields__lectures__group='row_3',
        fields__problem_classes__group='row_3',
        fields__coursework__group='row_3',
        fields__synoptic_lectures__group='row_3',
        fields__exams__group='row_3',
        fields__credit_hours__after='exams',
        fields__credit_hours__group='row_4',
        fields__exam_mark_fraction__group='row_4',
        fields__coursework_mark_fraction__group='row_4',
        auto__exclude=['is_active'],
    )
    # columns__coursework_mark_fraction__display_name = "Coursework",
    # columns__coursework_mark_fraction__group = "Mark fraction",
    # columns__exam_mark_fraction__display_name = "Exam",
    # columns__exam_mark_fraction__group = "Mark fraction",
    #     html.p(
    #     lambda params, **_: format_html(f"<strong>General Notes:</strong> {params.module.notes}"),
    # ))
    # year = Form(
    #     auto__model=ModuleYear,
    #     instance=lambda params, **_: params.module.get_latest_year(),
    #     fields__academic_year__group="row_1",
    #     fields__students__group="row_1",
    #     fields__credit_hours__group="row_1",
    #     fields__lectures__group="row_2",
    #     fields__problem_classes__group="row_2",
    #     fields__courseworks__group="row_2",
    #     fields__synoptic_lectures__group="row_2",
    #     fields__exams__group="row_2",
    #     fields__dissertation_load_function__group="row_2",
    #     fields__exam_mark_fraction__group="row_3",
    #     fields__coursework_mark_fraction__group="row_3",
    #     fields__notes__group="row_3",
    #     auto__exclude=['module', 'academic_year'],
    # )

    tasks = Table(
        auto__model=Task,
        auto__exclude=['unit', 'is_active', 'description'],
        rows=lambda params, **_: Task.objects.filter(unit=params.unit),
        sortable=False,
        # columns__is_active__filter__include=True,
        # query__form__fields__is_active__initial=lambda **_: True,
        columns__name__cell__url=lambda row, **_: f'/task/{row.pk}',
        columns__edit=Column.edit(
            cell__url=lambda row, **_: f'/task/{row.pk}/edit/',
        ),
    )

    # module_years = Table(
    #     title="Previous Years",
    #     auto__model=ModuleYear,
    #     auto__exclude=['notes', 'module'],
    #     rows=lambda params, **_: ModuleYear.objects.filter(module=params.module),
    #     columns__dissertation_load_function__include=lambda params, **_: params.module.has_dissertation,
    #     columns__lectures__group="Load",
    #     columns__problem_classes__group="Load   ",
    #     columns__courseworks__group="Load",
    #     columns__synoptic_lectures__group="Load",
    #     columns__exams__group="Load",
    #     columns__dissertation_load_function__group="Load",
    #     columns__exam_mark_fraction__group="Mark Fraction",
    #     columns__coursework_mark_fraction__group="Mark Fraction",
    #     columns__academic_year__cell__url=lambda row, **_: f'/module_year/{row.pk}',
    # )

class UnitList(BasePage):
    """
    List of all currently active modules.
    """
    groups = Table(
        auto__model=Unit,
        auto__include=[
            'code', 'name', 'academic_group', 'students',
        ],
        columns__code__cell__url=lambda row, **_: row.get_absolute_url(),
        columns__code__filter__include=True,
        columns__name__cell__url=lambda row, **_: row.get_absolute_url(),
        columns__name__filter__include=True,
        columns__academic_group__cell__url=lambda row, **_: row.academic_group.get_absolute_url() if row.academic_group else None,
        columns__academic_group__filter__include=True,
        columns__task_open=Column(
            display_name="Open",
            sortable=False,
            group="Tasks",
            cell__value=lambda row, **_: 0 #row.task_set.count(),
        ),
        columns__task_assigned=Column(
            display_name="Assigned",
            sortable=False,
            group="Tasks",
            cell__value=lambda row, **_: 0 #sum(row.task_set.values_list('count', flat=True)),
        ),
        query_from_indexes=True,
        query__advanced__include=False,
    )


urlpatterns = [
    path('unit/<unit>/edit/', UnitEdit().as_view(), name='unit_edit'),
    path('unit/<unit>/', UnitDetail().as_view(), name='unit_detail'),
    path('unit/', UnitList().as_view(), name='unit_list'),
]