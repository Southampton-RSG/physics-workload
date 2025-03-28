"""
Handles the views for the Load Functions Groups
"""
from django.urls import path
from django.template import Template

from iommi import Page, Table, html, Form, EditTable, Column, Field, Fragment

from plotly.graph_objs import Layout, Figure, Scatter
from plotly.graph_objs.layout import XAxis, YAxis
from plotly.offline import plot

from dash_bootstrap_templates import load_figure_template
load_figure_template('bootstrap_dark')

from app.models import LoadFunction

from app.assets import mathjax_js
from app.pages.components.tables import ColumnModify
from app.pages.components.headers import HeaderInstanceEdit, HeaderInstanceCreate, HeaderInstanceDelete, \
    HeaderInstanceDetail, HeaderList
from app.style import floating_fields_style


class LoadFunctionDelete(Page):
    """
    Delete the load function
    """
    header = HeaderInstanceDelete(
        lambda params, **_: params.load_function.get_instance_header(),
    )
    detail_factors = Form.delete(
        h_tag=None,
        auto__model=LoadFunction, instance=lambda params, **_: params.load_function,
        fields__plot_minimum__group="Plot",
        fields__plot_maximum__group="Plot",
        iommi_style=floating_fields_style,
        assets=mathjax_js,
    )


class LoadFunctionCreate(Page):
    header = HeaderInstanceCreate(
        lambda params, **_: params.load_function.get_model_header(),
    )
    form = Form.create(
        h_tag=None, auto__model=LoadFunction,
        fields__plot_minimum__group="Plot",
        fields__plot_maximum__group="Plot",
        iommi_style=floating_fields_style,
        editable=True,
    )


class LoadFunctionEdit(Page):
    """
    Edit the standard load
    """
    header = HeaderInstanceEdit(
        lambda params, **_: params.load_function.get_instance_header(),
    )
    detail_factors = Form.edit(
        h_tag=None,
        auto__model=LoadFunction, instance=lambda params, **_: params.load_function,
        fields__plot_minimum__group="Plot",
        fields__plot_maximum__group="Plot",
        iommi_style=floating_fields_style,
        editable=True,
        assets=mathjax_js,
        extra__redirect_to='..',
    )
    p = html.p(
        template="app/load_function/examples.html"
    )


class LoadFunctionDetail(Page):
    """
    Shows details of the standard load
    """
    header = HeaderInstanceDetail(
        lambda params, **_: params.load_function.get_instance_header()
    )
    detail = Form(
        auto__model=LoadFunction, instance=lambda params, **_: params.load_function,
        auto__exclude=['name'],
        fields__plot_minimum=dict(
            group="Plot",
            include=lambda params, **_: params.load_function.plot_minimum,
        ),
        fields__plot_maximum=dict(
            group="Plot",
            include=lambda params, **_: params.load_function.plot_maximum,
        ),
        iommi_style=floating_fields_style,
        editable=False,
    )
    plot = Template("{{plotly | safe }}")

    @staticmethod
    def create_graph(load_function: LoadFunction) -> str:
        """
        Creates a graph of the student load function
        :param load_function:
        :return:
        """
        if not load_function.plot_minimum:
            return ''

        student_range = list(range(load_function.plot_minimum, load_function.plot_maximum + 1))
        figure = Figure(
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
    header = HeaderList(
        lambda params, **_: LoadFunction.get_model_header()
    )
    list = Table(
        h_tag=None,
        auto__model=LoadFunction,
        rows=LoadFunction.available_objects.all(),
        auto__exclude=['notes'],
        columns__name__cell__url=lambda row, **_: row.get_absolute_url(),
        columns__expression__cell__template=Template("<td class='font-monospace'>{{ value | truncatechars:32 }}</td>"),
        columns__modify=ColumnModify.create(),
    )

def get_load_function_data(request, load_function):
    session_data = request.session.get('django_plotly_dash', {})
    session_data['x'] = [1, 2, 3]
    session_data['y'] = [1, 2, 3]
    return session_data


urlpatterns = [
    path('function/create/', LoadFunctionCreate().as_view(), name='load_function_create'),
    path('function/<load_function>/delete/', LoadFunctionDelete().as_view(), name='load_function_delete'),
    path('function/<load_function>/edit/', LoadFunctionEdit().as_view(), name='load_function_edit'),
    path('function/<load_function>/', LoadFunctionDetail(
        context__plotly=lambda params, **_: LoadFunctionDetail.create_graph(params.load_function),
    ).as_view(), name='load_function_detail'),
    path('function/', LoadFunctionList().as_view(), name='load_function_list'),
]
