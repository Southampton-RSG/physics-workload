"""

"""
from django.db.models import Count, Sum, Q, Case, When, Subquery, OuterRef
from django.urls import path
from django.utils.html import format_html
from django.template.loader import render_to_string

from iommi import Table, html, Form, Column, Field, LAST, Header, Asset, Action
from iommi.path import register_path_decoding

from app.forms.task import TaskForm
from app.forms.unit import UnitForm
from app.pages import BasePage, HeaderList, HeaderInstanceDetail, HeaderInstanceEdit, HeaderInstanceCreate, \
    HeaderInstanceDelete, create_modify_column
from app.models import Unit, Task, Assignment
from app.style import floating_fields_style


register_path_decoding(unit=lambda string, **_: Unit.objects.get(code=string))


class UnitTaskCreate(BasePage):
    """
    Create a task associated with a unit
    """
    header = Header(
        lambda params, **_: format_html(
            f"{params.unit.get_instance_header()} / Create Task "+render_to_string(
                "app/create_icon.html"
            )
        ),
    )
    form = TaskForm.create(
        h_tag=None,
        fields__unit=Field.non_rendered(
            initial=lambda params, **_: params.unit,
        ),
    )


class UnitDetail(BasePage):
    """
    View a unit and its associated tasks
    """
    header = Header(
        lambda params, **_: format_html(
            f"{params.unit.get_instance_header()}",
        ),
    )
    tasks = Table(
        h_tag=HeaderList,
        attrs__class={'mb-5': True},
        auto__model=Task,
        auto__include=[
            'name', 'number_needed', 'students',
            'load_calc', 'load_calc_first', 'assignment_set'
        ],
        rows=lambda params, **_: params.unit.task_set.all(),
        sortable=False,
        columns__load_calc=dict(
            group='Load',
            display_name='Normal',
        ),
        columns__load_calc_first=dict(
            group='Load',
            display_name='First time',
        ),
        columns__assignment_set=dict(
            cell__template='app/unit/assignment_set.html',
        ),
        columns__name__cell__url=lambda row, **_: row.get_absolute_url(),
        columns__modify=create_modify_column(),
    )
    form = UnitForm(
        title="Details",
        h_tag=HeaderInstanceDetail,
        instance=lambda params, **_: params.unit,
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


class UnitEdit(BasePage):
    """
    Edit a unit's details
    """
    header = HeaderInstanceEdit(
        lambda params, **_: format_html(
            f"{params.unit.get_instance_header()}"
        )
    )
    form = UnitForm.edit(
        h_tag=None,
        instance=lambda params, **_: params.unit,
    )


class UnitCreate(BasePage):
    """
    Page showing a unit to be created
    """
    header = HeaderInstanceCreate(
        lambda params, **_: format_html(
            Unit.get_model_header()
        ),
    )
    form = UnitForm.create(
        h_tag=None,
    )


class UnitList(BasePage):
    """
    List of all currently active modules.
    """
    header = HeaderList(
        lambda params, **_: format_html(
            Unit.get_model_header()
        )
    )
    list = Table(
        auto__model=Unit,
        auto__include=['code', 'name', 'academic_group', 'task_set', 'students'],
        columns__code=dict(
            cell__url=lambda row, **_: row.get_absolute_url(),
            filter__include=True,
        ),
        columns__name=dict(
            cell__url=lambda row, **_: row.get_absolute_url(),
            filter__include=True,
        ),
        columns__task_open=Column(
            display_name='Open',
            group='Tasks',
            filter__include=True,
            after='students',
        ),
        columns__task_set=dict(
            display_name='List',
            group='Tasks',
            cell__template='app/unit/task_set.html',
            after='task_open',
        ),
        columns__task_provisional=Column(),
        query=dict(
            filters=dict(
                task_open__value_to_q=lambda value_string_or_f, **_: Q(
                    task_open__gte=int(value_string_or_f)
                ),
                task_has_any_provisional__value_to_q=lambda value_string_or_f, **_: Q(
                    task_provisional__gte=1 if value_string_or_f == '1' else 0
                ),
            ),
            form=dict(
                fields__task_open=Field.integer(
                    display_name='Open Tasks',
                    input__attrs__type='number',
                ),
                fields__task_has_any_provisional=Field.boolean(
                    display_name=format_html(
                        "Has Any Provisional <i class='fa-solid fa-clipboard-question'></i>",
                    )
                ),
                actions__reset=Action.button(display_name='Clear Filter', attrs__type='reset'),
            ),
        ),
        rows=lambda params, **_: Unit.objects_active.annotate(
            assignment_count=Count('task_set__assignment_set'),
            task_count=Sum('task_set__number_needed'),
            task_open=Sum('task_set__number_needed')-Count('task_set__assignment_set'),
            task_provisional=Subquery(
                Assignment.objects.filter(
                    is_provisional=True,
                    task__unit__pk=OuterRef('pk')
                ),
                output_field=IntegerField(),
            ),
        ),
        page_size=20,
        h_tag=None,
        query__advanced__include=False,
        iommi_style=floating_fields_style,
    )


urlpatterns = [
    path('unit/create/', UnitCreate().as_view(), name='unit_create'),
    path('unit/<unit>/create/', UnitTaskCreate().as_view(), name='unit_task_create'),
    path('unit/<unit>/edit/', UnitEdit().as_view(), name='unit_edit'),
    path('unit/<unit>/', UnitDetail().as_view(), name='unit_detail'),
    path('unit/', UnitList().as_view(), name='unit_list'),
]