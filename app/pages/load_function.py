"""
Handles the views for the Load Functions Groups
"""
from typing import List
from django.template import Template

from iommi import Page, Table, html, Header

from plotly.graph_objs import Layout, Figure, Scatter
from plotly.graph_objs.layout import XAxis, YAxis
from plotly.offline import plot

from dash_bootstrap_templates import load_figure_template
load_figure_template('bootstrap_dark')

from app.models import LoadFunction
from app.forms.load_function import LoadFunctionForm
from app.pages.components.suffixes import SuffixCreate, SuffixEdit, SuffixDelete


class LoadFunctionCreate(Page):
    """
    Create a new load function
    """
    header = Header(
        lambda params, **_: LoadFunction.get_model_header_singular(),
        children__suffix=SuffixCreate(),
    )
    form = LoadFunctionForm.create()
    examples = html.p(
        template="app/load_function/examples.html"
    )


class LoadFunctionDelete(Page):
    """
    Delete the load function
    """
    header = Header(
        lambda params, **_: params.load_function.get_instance_header(),
        children__suffix=SuffixDelete(),
    )
    form = LoadFunctionForm.delete(
        instance=lambda params, **_: params.load_function,
        fields__name__include=False,  # Name is in the header
    )


class LoadFunctionEdit(Page):
    """
    Edit a load function
    """
    header = Header(
        lambda params, **_: params.load_function.get_instance_header(),
        children__suffix=SuffixEdit(),
    )
    form = LoadFunctionForm.edit(
        instance=lambda params, **_: params.load_function,
        extra__redirect_to='..',
    )
    examples = html.p(
        template="app/load_function/examples.html"
    )


class LoadFunctionDetail(Page):
    """
    Shows details of the standard load
    """
    header = Header(
        lambda params, **_: params.load_function.get_instance_header()
    )
    form = LoadFunctionForm(
        instance=lambda params, **_: params.load_function,
        fields=dict(
            name__include=False,
            plot_minimum=dict(
                include=lambda params, **_: params.load_function.plot_minimum,
            ),
            plot_maximum=dict(
                include=lambda params, **_: params.load_function.plot_maximum,
            ),
        ),
        editable=False,
    )
    plotly = Template("{{ page.extra_evaluated.plotly | safe }}")

    class Meta:
        @staticmethod
        def extra_evaluated__plotly(params, **_) -> str:
            """
            Creates a graph of the student load function.

            :param params: The page parameters, including the load function it's for.
            :return: A div containing the rendered plot (or an empty string if no plot is needed).
            """
            load_function: LoadFunction = params.load_function
            if not load_function.plot_minimum:
                # Nothing to show!
                return ''

            student_range: List[float] = list(range(load_function.plot_minimum, load_function.plot_maximum + 1))
            figure: Figure = Figure(
                data=[
                    Scatter(
                        x=student_range,
                        y=[load_function.evaluate(x) for x in student_range],
                    ),
                ],
                layout=Layout(
                    template='bootstrap_dark',
                    xaxis=XAxis(title='Students'),
                    yaxis=YAxis(title='Load hours'),
                ),
            )
            return plot(figure, output_type='div')


class LoadFunctionList(Page):
    """
    Page listing the standard load over history
    """
    header = Header(
        lambda params, **_: LoadFunction.get_model_header()
    )
    list = Table(
        h_tag=None,
        auto__model=LoadFunction,
        auto__exclude=['notes', 'is_removed'],
        columns__name__cell__url=lambda row, **_: row.get_absolute_url(),
        columns__expression__cell__template=Template("<td class='font-monospace'>{{ value | truncatechars:32 }}</td>"),
        columns__plot_minimum=dict(
            group="Plot",
            display_name="Minimum",
        ),
        columns__plot_maximum=dict(
            group="Plot",
            display_name="Maximum",
        ),
        rows=LoadFunction.available_objects.all(),
    )


