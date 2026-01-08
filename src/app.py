from dash import html, dcc, Output, Input, State

from server import app
from pages import data_entry, results

app.layout = html.Div([
    dcc.Location(id="url"),

    # Session storage
    dcc.Store(id="session-input-data", storage_type="session"),  # Stores user input data
    dcc.Store(id="navigation-trigger", storage_type="memory"),  # Allows navigation between tabs

    # Page layout
    html.H1('Exposure Assessment Dashboard'),
    dcc.Tabs(id="navigation-tabs", children=[
        dcc.Tab(label='Data entry', value='data-entry'),
        dcc.Tab(label='Exposure results', value='exposure-results', id='results-tab', disabled=True),
    ]),
    html.Div(id="page-content")  # Placeholder for page content
])


@app.callback(
    Output("page-content", "children"),
    Input("navigation-tabs", "value"),
    State('session-input-data', 'data')
)
def render_main_content(tab, session_data):
    if tab == "data-entry":
        return data_entry.layout(session_data)
    elif tab == "exposure-results":
        return results.layout(session_data)

    raise ValueError("Invalid tab")


if __name__ == "__main__":
    app.run(debug=True)
