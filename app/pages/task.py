"""

"""
import string

from django.template.loader import render_to_string
from django.urls import path
from django.utils.html import format_html
from django.template import Template

from iommi import Page, Table, html, Form, EditTable, Column
from iommi.path import register_path_decoding
from iommi import register_search_fields
from iommi.views import crud_views


from app.models import Unit, Task, Assignment
from app.pages import BasePage, HeaderInstanceDelete, HeaderInstanceEdit, HeaderInstanceDetail
from app.forms.task import TaskForm
from app.style import floating_fields_style

register_path_decoding(task=lambda string, **_: Task.objects.get(pk=int(string)))
register_search_fields(model=Task, search_fields=['name'], allow_non_unique=True)


class TaskDetail(BasePage):
    """
    Page for showing task details
    """
    header = HeaderInstanceDetail(
        lambda params, **_: format_html(
            f"{params.task.get_instance_header()}"
        )
    )
    list = EditTable(
        auto__model=Assignment,
        auto__exclude=['notes', 'task'],
        columns__staff__field=dict(
            include=True,
        ),
        columns__is_first_time__field=dict(
            include=True,
        ),
        columns__is_provisional__field__include=True,
        rows=lambda params, **_: params.task.assignment_set.all(),
    )
    br = html.br()

    form = TaskForm(
        title="Details",
        instance=lambda params, **_: params.task,
        editable=False,
    )

class TaskEdit(BasePage):
    """
    Page for editing a task
    """
    header = HeaderInstanceEdit(
        lambda params, **_: format_html(
            f"{params.task.get_instance_header()}"
        )
    )
    form = TaskForm.edit(
        h_tag=None,
        instance=lambda params, **_: params.task,
    )


class TaskDelete(BasePage):
    """
    Page for deleting a task
    """
    header = HeaderInstanceDelete(
        lambda params, **_: format_html(
            f"{params.task.get_instance_header()}"
        )
    )
    form = TaskForm.delete(
        h_tag=None,
        instance=lambda params, **_: params.task,
    )

# class TaskPage(Page):
#     """
#
#     """
#     module = EditTable(
#         auto__model=Module,
#         sortable=False,
#         auto__exclude=['notes'],
#         rows=lambda params, **_: [params.module],
#         title=lambda params, **_: f"{params.module}",
#         columns__edit=Column.edit(
#             cell__url=lambda row, **_: f'/module/{row.pk}/edit/',
#         ),
#     )
#     module_notes = html.p(
#         lambda params, **_: format_html(f"<strong>General Notes:</strong> {params.module.notes}"),
#     )
#     year = Table(
#         auto__model=ModuleYear,
#         title=None,
#         sortable=False,
#         auto__exclude=['notes', 'module'],
#         columns__edit=Column.edit(
#             cell__url=lambda row, **_: f'/module_year/{row.pk}/edit/',
#         ),
#         rows=lambda params, **_: [ModuleYear.objects.filter(module=params.module).latest()],
#     )
#     year_notes = html.p(
#         lambda params, **_: format_html(f"<strong>Year Notes:</strong> {ModuleYear.objects.filter(module=params.module).latest().notes}"),
#     )
#
#     tasks = Table(
#         auto__model=Task,
#         auto__exclude=['module', 'is_active'],
#         sortable=False,
#         # columns__is_active__filter__include=True,
#         # query__form__fields__is_active__initial=lambda **_: True,
#         columns__name__cell__url=lambda row, **_: f'/task/{row.pk}',
#         columns__edit=Column.edit(
#             cell__url=lambda row, **_: f'/task/{row.pk}/edit/',
#         ),
#     )
#     years = Table(
#         title="Previous Years",
#         auto__model=ModuleYear,
#         rows=lambda params, **_: ModuleYear.objects.filter(module=params.module),
#         columns__dissertation_load_function__include=lambda params, **_: params.module.has_dissertation,
#         columns__module__include=False,
#         columns__notes__include=False,
#         columns__year__cell__url=lambda row, **_: f'/module_year/{row.pk}',
#     )
#
#
urlpatterns = [
    path('task/<task>/delete/', TaskDelete().as_view(), name='task_delete'),
    path('task/<task>/edit/', TaskEdit().as_view(), name='task_edit'),
    path('task/<task>/', TaskDetail().as_view(), name='task_detail'),
]