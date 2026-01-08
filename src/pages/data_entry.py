"""
Data entry page
"""
import base64
import json

from dash import html, dcc, dash_table, exceptions, callback, Input, Output, State

from data import get_categories_table

__all__ = ['layout']


def layout(session_data: list[dict] = None) -> html.Div:
    """Data entry page layout."""
    table_data = session_data_to_table_data(session_data)

    return html.Div(
        [
            html.P(
                "Enter use levels for each group below. Exposure results will "
                "become available once valid data has been provided."
            ),

            html.Div(
                [
                    html.Button("Reset", id="btn-reset"),
                    html.Button("Import input", id="btn-import"),
                    dcc.Upload('Upload a JSON file', id='import-inputs'),
                    html.Button("Export input", id="btn-export"),
                    dcc.Download(id='export-inputs', type='text/json'),
                    html.Button(
                        "Calculate exposure",
                        id="btn-calculate",
                        disabled=True,
                    ),
                ],
                style={"display": "flex", "gap": "10px", "marginBottom": "15px"},
            ),

            dash_table.DataTable(
                id="input-table",
                data=table_data,
                editable=True,
                row_deletable=False,
                style_cell={
                    "textAlign": "left",
                    "whiteSpace": "normal",
                    "height": "auto",
                },
                style_cell_conditional=[
                    {"if": {"column_id": "Group Code"}, "width": "120px"},
                    {"if": {"column_id": "Group Name"}, "width": "300px"},
                ],
                columns=[
                    {
                        "name": "Group code",
                        "id": "Group Code",
                        "editable": False,
                    },
                    {
                        "name": "Group name",
                        "id": "Group Name",
                        "editable": False,
                    },
                    {
                        "name": "Use level (mg/kg)",
                        "id": "Use level (mg/kg)",
                        "type": "numeric",
                        "editable": True,
                        "validation": {
                            "allow_null": True,
                            "default": None,
                        },
                    },
                    {
                        "name": "Consumers of",
                        "id": "Consumers of",
                        "presentation": "dropdown",
                        "editable": True,
                    },
                ],
                dropdown={
                    "Consumers of": {
                        "options": [
                            {"label": "Yes", "value": True},
                            {"label": "No", "value": False},
                        ]
                    }
                },
            ),
        ]
    )


@callback(
    Output("btn-calculate", "disabled", allow_duplicate=True),
    Output("input-table", "data", allow_duplicate=True),
    Input("input-table", "data"),
    prevent_initial_call='initial_duplicate',
)
def validate_table(table_data) -> tuple[bool, list[dict]]:
    # Enable "Calculate exposure" only if at least one row has Use level > 0
    enable_calculate = any(
        row.get("Use level (mg/kg)") is not None and row.get("Use level (mg/kg)") > 0
        for row in table_data
    )

    # Clear "Consumers of" if [Use level] <= 0
    for row in table_data:
        if row.get("Use level (mg/kg)") is None or row.get("Use level (mg/kg)") <= 0:
            row["Consumers of"] = False

    return not enable_calculate, table_data


@callback(
    Output("btn-calculate", "disabled"),
    Output("input-table", "data"),
    Input("btn-reset", "n_clicks"),
    prevent_initial_call=True,
)
def clear_table(_) -> tuple[bool, list[dict]]:
    """Reset the input table to its initial state."""
    reset_data = get_categories_table().to_dicts()
    return True, reset_data


def table_data_to_session_data(table_data: list[dict]) -> list[dict]:
    """Convert table input data into a minified session data object."""
    # We create a list of dicts with only the relevant fields and valid use levels
    return [
        {
            'group_code': row['Group Code'],
            'use_level': row['Use level (mg/kg)'],
            'consumers_of': row['Consumers of']
        }
        for row in table_data
        if row['Use level (mg/kg)'] is not None and row['Use level (mg/kg)'] > 0
    ]


def session_data_to_table_data(session_data: list[dict] = None) -> list[dict]:
    """Convert session input data back to table data format."""
    table_data = get_categories_table().to_dicts()
    if not session_data:
        return table_data

    session_data_map = {item['group_code']: item for item in session_data}

    for row in table_data:
        group_code = row['Group Code']
        if group_code in session_data_map:
            row['Use level (mg/kg)'] = session_data_map[group_code]['use_level']
            row['Consumers of'] = session_data_map[group_code]['consumers_of']
        else:
            row['Use level (mg/kg)'] = None
            row['Consumers of'] = False

    return table_data


@callback(
    Output('input-table', 'data', allow_duplicate=True),
    Input('import-inputs', 'contents'),
    config_prevent_initial_callbacks=True
)
def import_placeholder(contents: str):
    """Import input data from a JSON file"""
    # Placeholder for future file upload logic
    if contents is None:
        data = []
    else:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        data = json.loads(decoded)

    table_data = session_data_to_table_data(data)
    return table_data


@callback(
    Output('export-inputs', "data"),
    Input("btn-export", "n_clicks"),
    State("input-table", "data"),
    prevent_initial_call=True,
)
def export_placeholder(_, data):
    """Export input data to a JSON file"""
    # Placeholder for future file export logic
    exposure_input = table_data_to_session_data(data)
    return {
        'content': json.dumps(exposure_input),
        'filename': 'exposure_input.json',
    }


@callback(
    Output("session-input-data", "data"),
    Output("results-tab", "disabled"),
    Output("navigation-tabs", "value"),
    Input("btn-calculate", "n_clicks"),
    State("input-table", "data"),
    prevent_initial_call=True,
)
def calculate_exposure(n_clicks, table_data):
    """Save input data to session storage and enable results tab.

    Args:
        n_clicks: Ignored
        table_data: The user input data

    Returns:

    """
    # Only proceed if button was clicked
    if n_clicks is None:
        raise exceptions.PreventUpdate

    session_data = table_data_to_session_data(table_data)

    return session_data, False, "exposure-results"
