from datetime import datetime
from typing import Dict, Any, List

from django.template import Template
from iommi import Page, Header, html, Table, Column
from plotly.graph_objs import Figure, Scatter, Layout
from plotly.graph_objs.layout import XAxis, YAxis
from plotly.offline import plot

from app.forms.staff import StaffForm
from app.models import Staff, Assignment
from app.pages.components.suffixes import SuffixHistory
from app.style import get_balance_classes


class StaffHistoryDetail(Page):
    """
    View showing the detail of a staff member at a point in time.
    """
    header = Header(
        lambda staff, **_: staff.get_instance_header(),
        children__suffix=SuffixHistory(
             text=lambda staff_history, **_: f" / {staff_history.history_date.date()} "
        )
    )
    form = StaffForm(
        h_tag=None,
        auto=dict(
            instance=lambda staff, **_: staff,
            exclude=[
                'user', 'is_removed',
            ],
        ),
        fields=dict(
            fte_fraction__include=lambda staff_history, **_: staff_history.fte_fraction,
            hours_fixed__include=lambda staff_history, **_: staff_history.hours_fixed,
            notes__include=lambda request, **_: request.user.is_staff,
            load_target__group='row2',
            load_assigned__group = 'row2',
            load_external__group='row2',
            load_balance_final=dict(
                group='row3',
                after='load_external',
                non_editable_input__attrs__class=lambda staff_history, **_: {
                    'form-control-plaintext': True
                } | get_balance_classes(staff_history.load_balance_final),
            ),
            load_balance_historic=dict(
                group = 'row3',
                after='load_balance_final',
                initial=lambda staff_history, **_: staff_history.load_balance_historic,
                non_editable_input__attrs__class=lambda params, **_: {
                    'form-control-plaintext': True,
                } | get_balance_classes(params.staff.load_balance_historic),
            ),
        ),
        editable=False,
    )
    assignments = Table(
        auto=dict(
            model=Assignment,
            exclude=[
                'staff'
            ],
        ),
        columns = dict(
            is_removed__include=False,
            notes__include=False,
            task=dict(
                cell=dict(
                    value=lambda row, **_: row.task.get_name(),
                    url=lambda row, **_: row.task.get_absolute_url(),
                ),
            ),
            load_calc__after='task',
        ),
        rows=lambda staff, staff_history, **_: Assignment.history.as_of(staff_history.history_date).filter(staff=staff),
    )


class StaffHistoryList(Page):
    """
    List of History entries for a staff member.
    """
    header = Header(
        lambda staff, **_: staff.get_instance_header(),
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
                    attrs__class=lambda row, **_: {
                        'text-success': True if row.load_balance_historic <= -1 else False,
                        'text-danger': True if row.load_balance_historic >= 1 else False,
                    }
                ),
            ),
        ),
        rows=lambda staff, **_: staff.history.all(),
    )

    class Meta:
        @staticmethod
        def extra_evaluated__plot(
                params: Dict[str, Any],
                staff: Staff, **_
        ) -> str:
            """
            Creates a graph of the staff balance over time.

            :param params: The Iommi view params.
            :param staff: The Staff instance, provided via URL decoding.
            :return: The HTML code of the graph.
            """
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
