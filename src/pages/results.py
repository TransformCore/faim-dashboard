"""
Results page layout with sub-tabs for exposure analysis.
"""
from dash import html, dcc, Input, Output, callback

from .panes import exposure_results, graph_p975_exposure, graph_average_exposure, exposure_summary

__all__ = ['layout']


# Define the tabs and their corresponding actions
tabs = {
    'exposure-summary': {
        'title': 'Exposure summary',
        'action': exposure_summary
    },
    'exposure-results': {
        'title': 'Exposure results',
        'action': exposure_results
    },
    'graph-average-exposure': {
        'title': 'Graph average exposure',
        'action': graph_average_exposure
    },
    'graph-p975-exposure': {
        'title': 'Graph 97.5ᵗʰ percentile exposure',
        'action': graph_p975_exposure
    }
}


def layout(session_data: list[dict]) -> html.Div:
    return html.Div([
        dcc.Tabs(id="results-sub-tabs", value="exposure-summary", children=[
            dcc.Tab(label=data['title'], value=value) for value, data in tabs.items()
        ]),
        html.Div(id="sub-tab-content")
    ])


@callback(
    Output("sub-tab-content", "children"),
    Input("results-sub-tabs", "value"),
    Input("session-input-data", "data")
)
def render_sub_tab(tab, session_data: list[dict]) -> html.Div:
    if not session_data:
        raise ValueError('Data is required')

    if tab not in tabs.keys():
        raise ValueError('Tab not found')

    return tabs[tab]['action'].layout(session_data)
