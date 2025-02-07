"""

"""
from django.urls import path
from django.utils.html import format_html
from django.template import Template

from iommi import Page, Table, html, Form, EditTable, Column
from iommi.path import register_path_decoding
from iommi import register_search_fields
from iommi.views import crud_views

from app.models import Module, ModuleYear
from app.models.task import Task

register_path_decoding(module=lambda string, **_: Module.objects.get(code=string))
# register_search_fields(model=Task, search_fields=['name'], allow_non_unique=True)


class ModulePage(Page):
    """

    """
    module = Table(
        auto__model=Module,
        sortable=False,
        auto__exclude=['notes'],
        rows=lambda params, **_: [params.module],
        title=lambda params, **_: f"{params.module}",
        columns__edit=Column.edit(
            cell__url=lambda row, **_: f'/module/{row.pk}/edit/',
        ),
    )
    module_notes = html.p(
        lambda params, **_: format_html(f"<strong>General Notes:</strong> {params.module.notes}"),
    )
    year = Table(
        auto__model=ModuleYear,
        title=None,
        sortable=False,
        auto__exclude=['notes', 'module'],
        columns__edit=Column.edit(
            cell__url=lambda row, **_: f'/module_year/{row.pk}/edit/',
        ),
        rows=lambda params, **_: [ModuleYear.objects.filter(module=params.module).latest()],
    )
    year_notes = html.p(
        lambda params, **_: format_html(f"<strong>Year Notes:</strong> {ModuleYear.objects.filter(module=params.module).latest().notes}"),
    )

    tasks = Table(
        auto__model=Task,
        auto__exclude=['module', 'is_active'],
        sortable=False,
        # columns__is_active__filter__include=True,
        # query__form__fields__is_active__initial=lambda **_: True,
        columns__name__cell__url=lambda row, **_: f'/task/{row.pk}',
        columns__edit=Column.edit(
            cell__url=lambda row, **_: f'/task/{row.pk}/edit/',
        ),
    )
    years = Table(
        title="Previous Years",
        auto__model=ModuleYear,
        rows=lambda params, **_: ModuleYear.objects.filter(module=params.module),
        columns__dissertation_load_function__include=lambda params, **_: params.module.has_dissertation,
        columns__module__include=False,
        columns__notes__include=False,
        columns__year__cell__url=lambda row, **_: f'/module_year/{row.pk}',
    )


urlpatterns = [
    path('module/<module>/', ModulePage().as_view()),
    path('module/', crud_views(model=Module)),
    path('module_year/', crud_views(model=ModuleYear)),
    path('task/', crud_views(model=Task)),
]