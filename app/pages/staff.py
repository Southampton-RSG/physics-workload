"""
Handles the views for the Academic Groups
"""
from datetime import datetime
from typing import List, Dict, Any

from django.template import Template
from django.utils.html import format_html

from iommi import EditTable, EditColumn, Page, Field, Header, html, Table, Column, register_search_fields, LAST, Action


from plotly.graph_objs import Layout, Figure, Scatter
from plotly.graph_objs.layout import XAxis, YAxis
from plotly.offline import plot

from dash_bootstrap_templates import load_figure_template
load_figure_template('bootstrap_dark')

from app.auth import has_access_decoder
from app.models import Staff, Assignment, Task
from app.models.standard_load import StandardLoad
from app.forms.staff import StaffForm
from app.style import floating_fields_select2_inline_style, get_balance_classes
from app.tables.staff import StaffTable
from app.tables.assignment import AssignmentStaffTable
from app.pages.components.suffixes import SuffixCreate, SuffixEdit, SuffixDelete, SuffixHistory


class StaffDelete(Page):
    """

    """
    header = Header(
        lambda params, **_: params.staff.get_instance_header(),
        children__suffix=SuffixDelete(),
    )
    form = StaffForm.delete(
        h_tag=None,
        instance=lambda params, **_: params.staff,
        auto__exclude=['is_removed', 'user'],
        fields=dict(
            fte_fraction__include=lambda params, **_: params.staff.fte_fraction,
            hours_fixed__include=lambda params, **_: params.staff.hours_fixed,
            load_target__group='row2',
            load_assigned__group='row2',
            load_balance_historic__group='row2',
        )
    )


class StaffEdit(Page):
    """

    """
    header = Header(
        lambda params, **_: params.staff.get_instance_header(),
        children__suffix=SuffixEdit(),
    )
    form = StaffForm.edit(
        h_tag=None,
        auto__instance=lambda params, **_: params.staff,
        auto__exclude=Staff.DYNAMIC_FIELDS + ['is_removed', 'user'],
        fields=dict(
            load_external=dict(
                group='row25'
            ),
            load_balance=Field.integer(
                editable=False,
                group='row25',
                after='load_external',
                initial=lambda params, **_: int(params.staff.get_load_balance()),
                non_editable_input__attrs__class=lambda params, **_: {
                    'form-control-plaintext': True
                } | get_balance_classes(params.staff.get_load_balance()),
                help_text="Load assigned minus target load. Positive if overloaded."
            ),
        )
    )


class StaffCreate(Page):
    """
    Create a new staff member
    """
    header = Header(
        lambda params, **_: Staff.get_model_header_singular(),
        children__suffix=SuffixCreate(),
    )
    form = StaffForm.create(
        h_tag=None,
        auto__exclude=Staff.DYNAMIC_FIELDS + ['is_removed', 'user'],
        fields=dict(
            standard_load=Field.non_rendered(
                include=True,
                initial=lambda params, **_: StandardLoad.objects.latest(),
            )
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
        auto=dict(
            instance=lambda params, **_: params.staff,
            exclude=[
                'notes', 'user', 'is_removed', 'load_balance_final',
            ],
        ),
        fields=dict(
            fte_fraction__include=lambda params, **_: params.staff.fte_fraction,
            hours_fixed__include=lambda params, **_: params.staff.hours_fixed,
            load_target__group='row2',
            load_assigned__group='row2',
            load_external__group='row2',
            load_balance=Field.integer(
                group='row3',
                initial=lambda params, **_: int(params.staff.get_load_balance()),
                non_editable_input__attrs__class=lambda params, **_: {
                    'form-control-plaintext': True
                } | get_balance_classes(params.staff.get_load_balance()),
                help_text="Load assigned minus target load. Positive if overloaded."
            ),
            load_balance_historic=dict(
                group = 'row3',
                after='load_balance',
                initial=lambda params, **_: int(params.staff.load_balance_historic),
                non_editable_input__attrs__class=lambda params, **_: {
                    'form-control-plaintext': True,
                } | get_balance_classes(params.staff.get_load_balance()),
            ),
            notes=dict(
                include=lambda request, **_: request.user.is_staff,
                after=LAST,
                non_editable_input__attrs__class=lambda params, **_: {
                    'form-control-plaintext': True,
                },
            ),
        ),
        editable=False,
        actions__submit=None,
    )
    assignments = AssignmentStaffTable()


class StaffHistoryDetail(Page):
    """
    View showing the detail of a staff member at a point in time.
    """
    header = Header(
        lambda params, **_: params.staff.get_instance_header(),
        children__suffix=SuffixHistory(
             text=lambda params, **_: f" / {params.staff_history.history_date.date()} "
        )
    )
    form = StaffForm(
        h_tag=None,
        auto=dict(
            instance=lambda params, **_: params.staff,
            exclude=[
                'notes', 'user', 'is_removed', 'load_balance_final',
            ],
        ),
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
                'form-control-plaintext': True
            } | get_balance_classes(params.staff.get_load_balance()),
            help_text="Load assigned minus target load. Positive if overloaded."
        ),
        fields__load_balance_historic=dict(
            group = 'row3',
            after='load_balance',
            initial=lambda params, **_: int(params.staff.load_balance_historic),
            non_editable_input__attrs__class=lambda params, **_: {
                'form-control-plaintext': True,
            } | get_balance_classes(params.staff.load_balance_historic),
        ),
        editable=False,
        actions__submit=None,
    )


class StaffHistoryList(Page):
    """
    List of History entries for a staff member.
    """
    header = Header(
        lambda params, **_: params.staff.get_instance_header(),
        children__suffix=SuffixHistory(),
    )

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
        columns=dict(
            history_date=Column(
                cell=dict(
                    url=lambda params, row, **_: f"{row.history_id}/",
                    value=lambda params, row, **_: row.history_date.date(),
                ),
            ),
            history_id=Column(
                render_column=False,
            ),
            load_balance_final=dict(
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
            load_balance_historic=dict(
                after="load_balance_final",
                group="Load Balance",
                display_name="Cumulative",
                cell=dict(
                    value=lambda row, **_: int(row.load_balance_historic),
                    attrs__class=lambda row, **_: {
                        'text-success': True if row.load_balance_historic <= -1 else False,
                        'text-danger': True if row.load_balance_historic >= 1 else False,
                    }
                ),
            ),
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


register_search_fields(
     model=Staff,
    search_fields=['name', 'gender', 'academic_group'],
    allow_non_unique=True,
)
