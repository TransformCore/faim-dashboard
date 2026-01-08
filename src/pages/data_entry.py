"""
Data entry page
"""
import base64
import json

from dash import html, dcc, dash_table, exceptions, callback, callback_context, Input, Output, State

from data import get_categories_table

__all__ = ['layout']


def layout() -> html.Div:
    """Data entry page layout."""
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
                data=get_categories_table().to_dicts(),
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
    Output("btn-calculate", "disabled"),
    Output("input-table", "data"),
    Input("input-table", "data"),
    Input("btn-reset", "n_clicks"),
    Input("session-input-data", "data"),
    prevent_initial_call=True,
)
def validate_or_reset_table(table_data, _, session_data) -> tuple[bool, list[dict]]:
    """Validate or reset the input table, or restore from session data."""
    # If no trigger or triggered by page load, return current state
    if not callback_context.triggered:
        return True, table_data

    triggered_id = callback_context.triggered[0]["prop_id"].split(".")[0]

    if triggered_id == "btn-reset":
        return clear_table()

    # Restore data from session if available
    if triggered_id == "session-input-data" and session_data is not None:
        return restore_table_from_session(session_data)

    # Only validate if triggered by table data changes
    if triggered_id == "input-table":
        return validate_table(table_data)

    # Default case
    return True, table_data


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


def clear_table() -> tuple[bool, list[dict]]:
    reset_data = get_categories_table().to_dicts()
    return True, reset_data


def restore_table_from_session(session_data) -> tuple[bool, list[dict]]:
    """Restore table data from session storage."""
    try:
        # Start with the base categories table
        base_data = get_categories_table().to_dicts()

        # Create a mapping of group codes to session data
        session_map = {item['group_code']: item for item in session_data}

        # Update base data with session values
        for row in base_data:
            group_code = row['Group Code']
            if group_code in session_map:
                session_item = session_map[group_code]
                row['Use level (mg/kg)'] = session_item.get('use_level')
                row['Consumers of'] = session_item.get('consumers_of', False)

        # Validate the restored data
        return validate_table(base_data)

    except (KeyError, TypeError, AttributeError):
        # If session data is malformed, return clear table
        return clear_table()


def get_exposure_input(table_data) -> list[dict]:
    return [
        {
            'group_code': row['Group Code'],
            'use_level': row['Use level (mg/kg)'],
            'consumers_of': row['Consumers of']
        }
        for row in table_data
        if row['Use level (mg/kg)'] is not None and row['Use level (mg/kg)'] > 0
    ]


# @callback(
#     Output("btn-import", "n_clicks"),
#     Input('import-inputs', 'contents'),
#     config_prevent_initial_callbacks=True
# )
# def import_placeholder(contents: str):
#     """Import input data from a JSON file"""
#     # Placeholder for future file upload logic
#     if contents is None:
#         return
#
#     decoded = base64.b64decode(contents)
#     data = json.loads(decoded)
#     return 0

@callback(
    Output('export-inputs', "data"),
    Input("btn-export", "n_clicks"),
    State("input-table", "data"),
    prevent_initial_call=True,
)
def export_placeholder(_, data):
    """Export input data to a JSON file"""
    # Placeholder for future file export logic
    exposure_input = get_exposure_input(data)
    return {
        'content': json.dumps(exposure_input, indent=2),
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
def calculate_exposure(n_clicks, data):
    """Save input data to session storage and enable results tab.

    Args:
        n_clicks: Ignored
        data: The user input data

    Returns:

    """
    if n_clicks is None:
        raise exceptions.PreventUpdate

    exposure_input = get_exposure_input(data)

    return exposure_input, False, "exposure-results"
