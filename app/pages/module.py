"""

"""
from django.urls import path
from django.utils.html import format_html
from django.template import Template

from iommi import Page, Table, html, Form, EditTable, Column
from iommi.path import register_path_decoding
from iommi import register_search_fields
from iommi.views import crud_views

from app.models import Module, ModuleYear, Task, TaskYearModule


register_path_decoding(module=lambda string, **_: Module.objects.get(code=string))
# register_search_fields(model=Task, search_fields=['name'], allow_non_unique=True)


class EditTableNoAdd(EditTable):
    class Meta:
        edit_actions__add_row = None


class ModulePage(Page):
    """

    """
    title = html.h1(lambda params, **_: f"{params.module}")
    module = Form(
        auto__model=Module,
        instance=lambda params, **_: params.module,
        fields__name__group="row_1",
        fields__code__group="row_1",
        fields__academic_group__group="row_1",
        fields__has_dissertation__group='row_2',
        fields__has_placement__group='row_2',
        auto__exclude=['is_active'],
    )

    #     html.p(
    #     lambda params, **_: format_html(f"<strong>General Notes:</strong> {params.module.notes}"),
    # ))
    year = Form(
        auto__model=ModuleYear,
        instance=lambda params, **_: params.module.get_latest_year(),
        fields__academic_year__group="row_1",
        fields__students__group="row_1",
        fields__credit_hours__group="row_1",
        fields__lectures__group="row_2",
        fields__problem_classes__group="row_2",
        fields__courseworks__group="row_2",
        fields__synoptic_lectures__group="row_2",
        fields__exams__group="row_2",
        fields__dissertation_load_function__group="row_2",
        fields__exam_mark_fraction__group="row_3",
        fields__coursework_mark_fraction__group="row_3",
        fields__notes__group="row_3",
        auto__exclude=['module', 'academic_year'],
    )

    tasks = Table(
        auto__model=Task,
        auto__exclude=['module', 'is_active'],
        rows=lambda params, **_: Task.objects.filter(module=params.module),
        sortable=False,
        # columns__is_active__filter__include=True,
        # query__form__fields__is_active__initial=lambda **_: True,
        columns__name__cell__url=lambda row, **_: f'/task/{row.pk}',
        columns__edit=Column.edit(
            cell__url=lambda row, **_: f'/task/{row.pk}/edit/',
        ),
    )

    module_years = Table(
        title="Previous Years",
        auto__model=ModuleYear,
        auto__exclude=['notes', 'module'],
        rows=lambda params, **_: ModuleYear.objects.filter(module=params.module),
        columns__dissertation_load_function__include=lambda params, **_: params.module.has_dissertation,
        columns__lectures__group="Load",
        columns__problem_classes__group="Load   ",
        columns__courseworks__group="Load",
        columns__synoptic_lectures__group="Load",
        columns__exams__group="Load",
        columns__dissertation_load_function__group="Load",
        columns__exam_mark_fraction__group="Mark Fraction",
        columns__coursework_mark_fraction__group="Mark Fraction",
        columns__academic_year__cell__url=lambda row, **_: f'/module_year/{row.pk}',
    )


urlpatterns = [
    path('module/<module>/', ModulePage().as_view(), name='module_detail'),
    path('module/', crud_views(model=Module)),
    path('module_year/', crud_views(model=ModuleYear)),
    path('task/', crud_views(model=Task)),
]