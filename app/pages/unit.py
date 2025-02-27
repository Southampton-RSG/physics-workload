"""

"""
from django.db.models import Count, Sum, Q
from django.urls import path
from django.utils.html import format_html
from django.template.loader import render_to_string

from iommi import Table, html, Form, Column, Field, LAST, Header
from iommi.path import register_path_decoding

from app.pages import BasePage, HeaderCreate, HeaderEdit, HeaderEditSuffix, HeaderCreateSuffix
from app.models import Unit, Task


register_path_decoding(unit=lambda string, **_: Unit.objects.get(code=string))


class UnitTaskCreate(BasePage):
    header = HeaderCreateSuffix(
        lambda params, **_: format_html(
            f"{params.unit.get_instance_header()} / Tasks "
        ),
    )


class UnitDetail(BasePage):
    """
    View a unit and its associated tasks
    """
    header = Header(
        lambda params, **_: format_html(
            f"{params.unit.get_instance_header()}",
        )
    )

    tasks = Table(
        h_tag=HeaderCreate,
        # h_tag=dict(
        #     attrs__class={'position-relative': True},
        #     children__create=html.span(template='app/create_button.html'),
        # ),
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
        columns__edit=Column(
            cell__url=lambda row, **_: f'{row.get_absolute_url()}edit/',
            cell__value=lambda row, **_: render_to_string('app/edit_icon.html'),
            after=LAST,
        ),
    )

    form = Form(
        title="Details",
        h_tag=HeaderEdit,
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
    )

    class Meta:
        iommi_style = 'floating_fields'


class UnitEdit(BasePage):
    """
    Edit a unit's details
    """
    header = HeaderEditSuffix(
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

    # tasks = Table(
    #     auto__model=Task,
    #     auto__exclude=['unit', 'is_active', 'description'],
    #     rows=lambda params, **_: Task.objects.filter(unit=params.unit),
    #     sortable=False,
    #     # columns__is_active__filter__include=True,
    #     # query__form__fields__is_active__initial=lambda **_: True,
    #     columns__name__cell__url=lambda row, **_: f'/task/{row.pk}',
    #     columns__edit=Column.edit(
    #         cell__url=lambda row, **_: f'/task/{row.pk}/edit/',
    #     ),
    # )

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

    class Meta:
        iommi_style = 'floating_fields'


class UnitCreate(BasePage):
    """
    Page showing a unit to be created
    """
    header = HeaderCreateSuffix(
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
    )

    class Meta:
        iommi_style = 'floating_fields'


class UnitList(BasePage):
    """
    List of all currently active modules.
    """
    header = HeaderCreate(
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
        query__form__fields__task_open=Field.number(
            display_name='Open Tasks',
        ),
        query__filters__task_open__value_to_q=lambda value_string_or_f, **_: Q(task_open__gte=int(value_string_or_f)),
        query__form__fields__task_provisional=Field.boolean(
            display_name='Provisional Assignments',
        ),
        query__filters__task_provisional__value_to_q=lambda value_string_or_f, **_: Q(task_provisional__gte=1 if value_string_or_f=='1' else 0),

        rows=lambda params, **_: Unit.objects_active.annotate(
            assignment_count=Count('task_set__assignment_set'),
            task_count=Sum('task_set__number_needed'),
            task_open=Sum('task_set__number_needed')-Count('task_set__assignment_set'),
            task_provisional=Count('task_set__assignment_set__is_provisional'),
        ),

        page_size=20,
        h_tag=None,
        query__advanced__include=False,
    )

    class Meta:
        # We want the fields for the filter to be floating
        iommi_style = 'floating_fields'


urlpatterns = [
    path('unit/create/', UnitCreate().as_view(), name='unit_create'),
    path('unit/<unit>/create/', UnitTaskCreate().as_view(), name='unit_task_create'),
    path('unit/<unit>/edit/', UnitEdit().as_view(), name='unit_edit'),
    path('unit/<unit>/', UnitDetail().as_view(), name='unit_detail'),
    path('unit/', UnitList().as_view(), name='unit_list'),
]