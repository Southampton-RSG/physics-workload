"""

"""
from django.db.models import Count, Sum, Q
from django.urls import path
from django.utils.html import format_html
from django.template.loader import render_to_string

from iommi import Table, html, Form, Column, Field, LAST, Header, Asset, Action
from iommi.path import register_path_decoding

from app.forms.task import TaskForm
from app.pages import BasePage, HeaderList, HeaderInstanceDetail, HeaderInstanceEdit, HeaderInstanceCreate, \
    HeaderInstanceDelete
from app.models import Unit, Task
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
            'load', 'load_first', 'assignment_set'
        ],
        rows=lambda params, **_: params.unit.task_set.all(),
        sortable=False,
        columns__load=dict(
            group='Load',
            display_name='Normal',
        ),
        columns__load_first=dict(
            group='Load',
            display_name='First time',
        ),
        columns__assignment_set=dict(
            cell__template='app/unit/assignment_set.html',
        ),
        columns__name__cell__url=lambda row, **_: row.get_absolute_url(),
        columns__modify=Column(
            # include=lambda request, **_: request.user.is_staff,
            cell__value=lambda row, **_: row.get_absolute_url(),
            cell__template='app/modify_row.html',
            cell__attrs__class={'text-center': True},
            header__attrs__class={'text-center': True},
            after=LAST,
        ),
    )

    form = Form(
        title="Details",
        h_tag=HeaderInstanceDetail,
        auto__model=Unit, instance=lambda params, **_: params.unit,
        auto__exclude=['is_active', 'task_set'],
        fields__code__group="Basics",
        fields__name__group="Basics",
        fields__academic_group__group="Basics",
        fields__students__group='Basics',
        fields__lectures__group = 'Sessions',
        fields__problem_classes__group = 'Sessions',
        fields__coursework__group = 'Sessions',
        fields__synoptic_lectures__group = 'Sessions',
        fields__exams__group='Sessions',
        fields__credit_hours__group='Credit',
        fields__exam_mark_fraction__group='Credit',
        fields__coursework_mark_fraction__group='Credit',
        fields__has_dissertation__group='Credit',
        fields__has_placement__group='Credit',
        editable=False,
        iommi_style=floating_fields_style,
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

    form = Form.edit(
        h_tag=None,
        auto__model=Unit, instance=lambda params, **_: params.unit,
        auto__exclude=['is_active', 'task_set'],
        fields__code__group="Basics",
        fields__name__group="Basics",
        fields__academic_group__group="Basics",
        fields__students__group='Basics',
        fields__lectures__group = 'Sessions',
        fields__problem_classes__group = 'Sessions',
        fields__coursework__group = 'Sessions',
        fields__synoptic_lectures__group = 'Sessions',
        fields__exams__group='Sessions',
        fields__credit_hours__group='Credit',
        fields__exam_mark_fraction__group='Credit',
        fields__coursework_mark_fraction__group='Credit',
        fields__has_dissertation__group='Credit',
        fields__has_placement__group='Credit',
        iommi_style='floating_fields'
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


class UnitCreate(BasePage):
    """
    Page showing a unit to be created
    """
    header = HeaderInstanceCreate(
        lambda params, **_: format_html(
            Unit.get_model_header()
        ),
    )

    form = Form.create(
        h_tag=None,
        auto__model=Unit,
        auto__exclude=['is_active', 'task_set'],
        fields__code__group="row1",
        fields__name__group="row1",
        fields__academic_group__group="row1",
        fields__has_dissertation__group='row2',
        fields__has_placement__group='row2',
        fields__students__group='row2',
        fields__credit_hours__group = 'row2',
        fields__lectures__group = 'row3',
        fields__problem_classes__group = 'row3',
        fields__coursework__group = 'row3',
        fields__synoptic_lectures__group = 'row3',
        fields__exams__group='row3',
        fields__exam_mark_fraction__group='row4',
        fields__coursework_mark_fraction__group='row4',
        iommi_style=floating_fields_style,
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
            cell__template='app/list_cell_name.html',
            after='task_open',
        ),
        query=dict(
            filters=dict(
                task_open__value_to_q=lambda value_string_or_f, **_: Q(
                    task_open__gte=int(value_string_or_f)
                ),
                task_provisional__value_to_q=lambda value_string_or_f, **_: Q(
                    task_provisional__gte=1 if value_string_or_f == '1' else 0
                ),
            ),
            form=dict(
                fields__task_open=Field.integer(
                    display_name='Open Tasks',
                    input__attrs__type='number',
                ),
                fields__task_provisional=Field.boolean(
                    display_name=format_html(
                        "Has Provisional <i class='fa-solid fa-clipboard-question'></i>",
                    )
                ),
                actions__reset=Action.button(display_name='Clear Filter', attrs__type='reset'),
            ),
        ),
        rows=lambda params, **_: Unit.objects_active.annotate(
            assignment_count=Count('task_set__assignment_set'),
            task_count=Sum('task_set__number_needed'),
            task_open=Sum('task_set__number_needed')-Count('task_set__assignment_set'),
            task_provisional=Count('task_set__assignment_set__is_provisional'),
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