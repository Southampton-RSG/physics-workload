from logging import Logger, getLogger
from typing import List

from django.template import Template
from django.utils import timezone
from iommi import Column, Header, Page, Table, html
from plotly.graph_objs import Bar, Figure, Layout, Scatter
from plotly.graph_objs.layout import XAxis, YAxis
from plotly.offline import plot

from app.models import AcademicGroup
from app.pages.components.suffixes import SuffixHistory
from app.style import get_balance_classes
from app.utility import year_to_academic_year

logger: Logger = getLogger(__name__)


class AcademicGroupHistoryList(Page):
    """
    List of History entries for an academic group.
    """

    header = Header(
        lambda academic_group, **_: academic_group.get_instance_header(),
        children__suffix=SuffixHistory(),
    )

    plot = html.div(
        attrs__class={"mt-4": True}, children=dict(header=Header("Load Balance"), graph=Template("{{page.extra_evaluated.plot | safe }}"))
    )

    list = Table(
        auto__model=AcademicGroup,
        h_tag=None,
        auto__include=["load_balance_final", "load_balance_historic"],
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
            load_balance_historic=dict(
                after="history_date",
                cell=dict(
                    attrs__class=lambda row, **_: get_balance_classes(row.load_balance_historic),
                ),
                display_name="Historic",
                group="Load Balance",
            ),
            load_balance_final=dict(
                after="load_balance_historic",
                cell=dict(
                    attrs__class=lambda row, **_: get_balance_classes(row.load_balance_final),
                ),
                group="Load Balance",
                display_name="Final",
            ),
            load_balance_cumulative=Column(
                after="load_balance_final",
                cell=dict(
                    value=lambda row, **_: row.load_balance_historic + row.load_balance_final,
                    attrs__class=lambda row, **_: get_balance_classes(row.load_balance_historic + row.load_balance_final),
                ),
                display_name="Cumulative",
                group="Load Balance",
                sortable=False,
            ),
        ),
        rows=lambda academic_group, **_: academic_group.history.all(),
    )

    class Meta:
        @staticmethod
        def extra_evaluated__plot(academic_group: AcademicGroup, **_) -> str:
            """
            Creates a graph of the staff balance over time.

            :param staff: The Staff instance, provided via URL decoding.
            :return: The HTML code of the graph.
            """
            dates: List[str] = []
            balance_cumulative: List[float] = []
            balance_yearly: List[float] = []

            for academic_group_historic in academic_group.history.order_by("history_date").all():
                dates.append(year_to_academic_year(academic_group_historic.history_date))

                this_year: int = academic_group_historic.load_balance_final
                previous_years: int = academic_group_historic.load_balance_historic
                cumulative_at_end: int = this_year + previous_years

                balance_yearly.append(this_year)
                balance_cumulative.append(cumulative_at_end)

            dates.append(year_to_academic_year(timezone.now()))
            balance_cumulative.append(academic_group.load_balance_historic + academic_group.get_load_balance())
            balance_yearly.append(academic_group.get_load_balance())

            figure: Figure = Figure(
                data=[
                    Bar(
                        x=dates,
                        y=balance_yearly,
                        name="Yearly",
                    ),
                    Scatter(
                        x=dates,
                        y=balance_cumulative,
                        name="Cumulative",
                    ),
                ],
                layout=Layout(
                    template="bootstrap_dark",
                    xaxis=XAxis(title="Date", fixedrange=True),
                    yaxis=YAxis(title="Load balance (hours)", fixedrange=True),
                    margin=dict(l=0, r=0, b=0, t=0, pad=0),
                ),
            )
            return plot(figure, output_type="div", config=dict(displayModeBar=False))
