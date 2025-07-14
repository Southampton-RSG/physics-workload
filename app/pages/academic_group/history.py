from datetime import datetime
from typing import Dict, Any, List

from django.template import Template
from iommi import Page, Header, html, Table, Column
from plotly.graph_objs import Figure, Scatter, Layout
from plotly.graph_objs.layout import XAxis, YAxis
from plotly.offline import plot

from app.models import AcademicGroup
from app.pages.components.suffixes import SuffixHistory
from app.style import get_balance_classes


class AcademicGroupHistoryList(Page):
    """
    List of History entries for an academic group.
    """
    header = Header(
        lambda academic_group, **_: academic_group.get_instance_header(),
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
        auto__model=AcademicGroup,
        h_tag=None,
        auto__include=['load_balance_final', 'load_balance_historic'],
        columns=dict(
            history_date=Column(
                cell=dict(
                    # url=lambda params, row, **_: f"{row.history_id}/",
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
        rows=lambda academic_group, **_: academic_group.history.all(),
    )

    class Meta:
        @staticmethod
        def extra_evaluated__plot(
                params: Dict[str, Any],
                academic_group: AcademicGroup, **_
        ) -> str:
            """
            Creates a graph of the staff balance over time.

            :param params: The Iommi view params.
            :param staff: The Staff instance, provided via URL decoding.
            :return: The HTML code of the graph.
            """
            dates: List[datetime] = [datetime.now()]
            balance_cumulative: List[float] = [academic_group.load_balance_historic+academic_group.get_load_balance()]
            balance_yearly: List[float] = [academic_group.get_load_balance()]

            for academic_group_historic in academic_group.history.all():
                dates.append(academic_group_historic.history_date)
                balance_cumulative.append(academic_group_historic.load_balance_historic)
                balance_yearly.append(academic_group_historic.load_balance_final)

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
