"""
Handles the views for the Academic Groups
"""
from datetime import datetime
from typing import List, Dict, Any

from django.urls import path
from django.template import Template

from iommi import EditTable, EditColumn, Page, Field, Header, html, Table, Column

from plotly.graph_objs import Layout, Figure, Scatter
from plotly.graph_objs.layout import XAxis, YAxis
from plotly.offline import plot

from dash_bootstrap_templates import load_figure_template
load_figure_template('bootstrap_dark')

from app.models import Staff, Assignment
from app.models.standard_load import StandardLoad
from app.forms.staff import StaffForm
from app.style import floating_fields_select2_inline_style
from app.tables.staff import StaffTable


class StaffDelete(Page):
    """

    """
    header = Header(lambda params, **_: params.staff.get_instance_header())
    form = StaffForm.delete(
        h_tag=None,
        instance=lambda params, **_: params.staff,
        auto__exclude=[
            'is_removed', 'user',
        ],
        fields__fte_fraction__include=lambda params, **_: params.staff.fte_fraction,
        fields__hours_fixed__include=lambda params, **_: params.staff.hours_fixed,
        fields__load_target__group='row2',
        fields__load_assigned__group='row2',
        fields__load_balance_historic__group='row2',
    )


class StaffEdit(Page):
    """

    """
    header = Header(lambda params, **_: params.staff.get_instance_header())
    form = StaffForm.edit(
        h_tag=None,
        auto__instance=lambda params, **_: params.staff,
        auto__exclude=[
            'load_target', 'load_assigned', 'load_balance_historic', 'is_removed', 'user',
        ],
    )


class StaffCreate(Page):
    """

    """
    header = Header(
        lambda params, **_: Staff.get_model_header_singular()
    )
    form = StaffForm.create(
        h_tag=None,
        auto__exclude=[
            'is_removed', 'user',
        ],
        fields__standard_load=Field.non_rendered(
            include=True,
            initial=lambda params, **_: StandardLoad.objects.latest(),
        )
    )


class StaffDetail(Page):
    """
    View showing the detail of a staff member
    """
    header = Header(
        lambda params, **_: params.staff.get_instance_header()
    )
    form = StaffForm(
        h_tag=None,
        auto__instance=lambda params, **_: params.staff,
        auto__exclude=[
            'notes', 'user', 'is_removed', 'load_balance_final',
        ],
        fields__fte_fraction__include=lambda params, **_: params.staff.fte_fraction,
        fields__hours_fixed__include=lambda params, **_: params.staff.hours_fixed,
        fields__notes__include=lambda request, **_: request.user.is_staff,
        fields__load_target__group='row2',
        fields__load_assigned__group = 'row2',
        fields__load_external__group='row2',
        fields__load_balance=Field.integer(
            group='row3',
            initial=lambda params, **_: int(params.staff.get_load_balance()),
            non_editable_input__attrs__class=lambda params, **_: {
                'form-control-plaintext': True,
                'text-success': True if params.staff.get_load_balance() <= 1 else False,
                'text-danger': True if params.staff.get_load_balance() >= 1 else False,
            },
            help_text="Load assigned minus target load. Positive if overloaded."
        ),
        fields__load_balance_historic=dict(
            group = 'row3',
            after='load_balance',
            initial=lambda params, **_: int(params.staff.load_balance_historic),
            non_editable_input__attrs__class=lambda params, **_: {
                'form-control-plaintext': True,
                'text-success': True if params.staff.load_balance_historic <= -1 else False,
                'text-danger': True if params.staff.load_balance_historic >= 1 else False,
            }
        ),
        editable=False,
        actions__submit=None,
    )
    assignments = EditTable(
        auto__model=Assignment,
        auto__exclude=['notes', 'load_calc', 'is_removed',],
        columns__task__field__include=True,
        columns__is_first_time__field__include=True,
        columns__is_provisional__field__include=True,
        columns__staff=EditColumn.hardcoded(
            render_column=False,
            field__parsed_data=lambda params, **_: params.staff,
        ),
        rows=lambda params, **_: Assignment.available_objects.filter(staff=params.staff),
        columns__delete=EditColumn.delete(),
        iommi_style=floating_fields_select2_inline_style,
    )


class StaffHistoryDetail(Page):
    """
    View showing the detail of a staff member at a point in time.
    """
    header = Header(
        lambda params, **_: params.staff.get_instance_header(suffix=f"{params.staff_history.history_date.date()}")
    )
    form = StaffForm(
        h_tag=None,
        auto__instance=lambda params, **_: params.staff,
        auto__exclude=[
            'notes', 'user', 'is_removed', 'load_balance_final',
        ],
        fields__fte_fraction__include=lambda params, **_: params.staff.fte_fraction,
        fields__hours_fixed__include=lambda params, **_: params.staff.hours_fixed,
        fields__notes__include=lambda request, **_: request.user.is_staff,
        fields__load_target__group='row2',
        fields__load_assigned__group = 'row2',
        fields__load_external__group='row2',
        fields__load_balance=Field.integer(
            group='row3',
            initial=lambda params, **_: int(params.staff.get_load_balance()),
            non_editable_input__attrs__class=lambda params, **_: {
                'form-control-plaintext': True,
                'text-success': True if params.staff.get_load_balance() <= 1 else False,
                'text-danger': True if params.staff.get_load_balance() >= 1 else False,
            },
            help_text="Load assigned minus target load. Positive if overloaded."
        ),
        fields__load_balance_historic=dict(
            group = 'row3',
            after='load_balance',
            initial=lambda params, **_: int(params.staff.load_balance_historic),
            non_editable_input__attrs__class=lambda params, **_: {
                'form-control-plaintext': True,
                'text-success': True if params.staff.load_balance_historic <= -1 else False,
                'text-danger': True if params.staff.load_balance_historic >= 1 else False,
            }
        ),
        editable=False,
        actions__submit=None,
    )


class StaffHistoryList(Page):
    """
    List of all currently active staff.
    """
    header = Header(lambda params, **_: params.staff.get_instance_header(suffix="History"))

    plot = html.div(
        attrs__class={"mt-4": True},
        children=dict(
            header=Header("Load Balance"),
            graph=Template("{{page.extra_evaluated.plot | safe }}")
        )
    )

    list = Table(
        auto__model=Staff,
        h_tag=None,
        auto__include=['load_balance_final', 'load_balance_historic'],
        columns__history_date=Column(
            cell=dict(
                url=lambda params, row, **_: f"{row.history_id}/",
                value=lambda params, row, **_: row.history_date.date(),
            ),
        ),
        columns__history_id=Column(
            render_column=False,
        ),
        columns__load_balance_final=dict(
            after="history_date",
            group="Load Balance",
            display_name="Final",
            cell=dict(
                value=lambda row, **_: int(row.load_balance_final),
                attrs__class=lambda row, **_: {
                    'text-success': True if row.load_balance_final <= -1 else False,
                    'text-danger': True if row.load_balance_final >= 1 else False,
                },
            ),
        ),
        columns__load_balance_historic=dict(
            after="load_balance_final",
            group="Load Balance",
            display_name="Cumulative",
            cell=dict(
                value=lambda row, **_: int(row.load_balance_historic),
                attrs__class=lambda row, **_: {
                    'text-success': True if row.load_balance_historic <= -1 else False,
                    'text-danger': True if row.load_balance_historic >= 1 else False,
                }
            )
        ),
        rows=lambda params, **_: params.staff.history.all(),
    )

    class Meta:
        @staticmethod
        def extra_evaluated__plot(
                params: Dict[str, Any], **_
        ) -> str:
            """
            Creates a graph of the staff balance over time.

            :param params: The Iommi view params.
            :return: The HTML code of the graph.
            """
            staff: Staff = params.staff
            dates: List[datetime] = [datetime.now()]
            balance_cumulative: List[float] = [staff.load_balance_historic+staff.get_load_balance()]
            balance_yearly: List[float] = [staff.get_load_balance()]

            for staff_historic in staff.history.all():
                dates.append(staff_historic.history_date)
                balance_cumulative.append(staff_historic.load_balance_historic)
                balance_yearly.append(staff_historic.load_balance_final)

            figure: Figure = Figure(
                data=[
                    Scatter(
                        x=dates,
                        y=balance_cumulative,
                        name="Cumulative"
                    ),
                    Scatter(
                        x=dates,
                        y=balance_yearly,
                        name="Yearly"
                    ),
                ],
                layout=Layout(
                    template='bootstrap_dark',
                    xaxis=XAxis(title='Date', fixedrange=True),
                    yaxis=YAxis(title='Balance (hours)', fixedrange=True),
                    margin=dict(l=0, r=0, b=0, t=0, pad=0),
                ),
            )
            return plot(
                figure,
                output_type='div',
                config=dict(
                    displayModeBar=False
                )
            )


class StaffList(Page):
    """
    List of all currently active staff.
    """
    header = Header(lambda params, **_: Staff.get_model_header())
    list = StaffTable(
        h_tag=None,
        rows=StaffTable.annotate_rows(Staff.available_objects),
    )


urlpatterns = [
    path('staff/create/', StaffCreate().as_view(), name='staff_create'),
    path('staff/<staff>/delete/', StaffDelete().as_view(), name='staff_delete'),
    path('staff/<staff>/edit/', StaffEdit().as_view(), name='staff_edit'),
    path('staff/<staff>/history/<staff_history>/', StaffHistoryDetail().as_view(), name='staff_history_detail'),
    path('staff/<staff>/history/', StaffHistoryList().as_view(), name='staff_history'),
    path('staff/<staff>/', StaffDetail(
        # context__plotly=lambda params, **_: StaffDetail.create_graph(params.staff),
    ).as_view(), name='staff_detail'),
    path('staff/', StaffList().as_view(), name='staff_list'),
]
