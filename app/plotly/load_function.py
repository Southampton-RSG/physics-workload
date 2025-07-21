from typing import Any, Dict

from dash import Output
from dash.dcc import Graph
from dash_bootstrap_components.themes import BOOTSTRAP
from django_plotly_dash import DjangoDash
from plotly.graph_objs import Figure, Layout, Scatter
from plotly.graph_objs.layout import XAxis, YAxis

app: DjangoDash = DjangoDash(
    name='LoadFunction',
    external_stylesheets=[BOOTSTRAP],
)
app.layout = Graph(id="load-function-graph", config={"displayModeBar": False})

@app.callback(
    Output("load-function-graph", "figure"),
)
def initialise_figure(
        session_state: Dict[str, Any],
        **kwargs,
) -> Figure:
    """
    Callback to render the overview as the user switches the target ratio
    """
    figure: Figure = Figure(
        data=[
            Scatter(
                x=session_state['students'],
                y=session_state['load_hours'],
            )
        ],
        layout=Layout(
            xaxis=XAxis("Students"),
            yaxis=YAxis("Load hours"),
        )
    )
    figure.update_layout()

    return figure

