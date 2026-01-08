import json
from pathlib import Path

import dash
from dash import Dash, html, dcc, dash_table, Input, Output, State, callback
import polars as pl

DATA_PATH = Path().resolve() / 'data' / 'combined_data.parquet'

df = pl.read_parquet(DATA_PATH)
app = Dash(__name__, suppress_callback_exceptions=True)


def get_categories_table(df: pl.DataFrame) -> pl.DataFrame:
    """Get the initial categories table with group codes and names."""
    df_categories = (
        df
        .select(['Group Code', 'Group Name'])
        .unique()
        .filter(pl.col('Group Code').str.contains(r'^\d+(\.\d+)*\.?$'))  # Remove group codes that don't look like x.y.z
        .with_columns(  # Sort lexicographically by group code
            pl.col("Group Code")
            .str.strip_chars(".")
            .str.split(".")
            .list.eval(pl.element().cast(pl.Int64))
            .alias("_sort_key")
        )
        .sort("_sort_key")
        .drop("_sort_key")
    )

    # The initial values for the input table
    df_init = df_categories.with_columns([
        pl.lit(None).alias('Use level (mg/kg)'),
        pl.lit(False).alias('Consumers of')
    ])

    return df_init


df_input = get_categories_table(df)


app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),

        # Session storage
        dcc.Store(id="session-input-data", storage_type="session"),
        dcc.Store(id="navigation-trigger", storage_type="memory"),

        html.H1("Exposure Assessment Dashboard"),

        dcc.Tabs(
            id="navigation-tabs",
            value="data-entry",
            children=[
                dcc.Tab(
                    label="Data entry",
                    value="data-entry"
                ),
                dcc.Tab(
                    label="Exposure results",
                    value="exposure-results",
                    id="results-tab",
                    disabled=True,
                ),
            ],
        ),

        html.Div(id="page-content"),
    ],
    style={"maxWidth": "1200px", "margin": "0 auto"},
)


def data_entry_layout():
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
                    html.Button("Export input", id="btn-export"),
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
                data=df_input.to_dicts(),
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


def exposure_results_layout():
    return html.Div(
        [
            html.H2("Exposure Results"),
            html.P("Exposure results will be displayed here."),
        ]
    )

# ------------------------------------------------------------------------------
# Page Routing
# ------------------------------------------------------------------------------

@callback(
    Output("page-content", "children"),
    Input("navigation-tabs", "value"),
    prevent_initial_call=False,
)
def render_page(tab):
    """Render the appropriate page layout based on the selected tab."""
    if tab == "data-entry":
        return data_entry_layout()

    if tab == "exposure-results":
        return exposure_results_layout()

    raise ValueError("Unknown tab selected")

# ------------------------------------------------------------------------------
# Enable / Disable "Calculate exposure" and Consumers dropdown
# ------------------------------------------------------------------------------

@callback(
    Output("btn-calculate", "disabled"),
    Output("input-table", "data"),
    Input("input-table", "data"),
    Input("btn-reset", "n_clicks"),
    prevent_initial_call=True,
)
def validate_or_reset_table(table_data, reset_clicks):
    ctx = dash.callback_context

    # If no trigger or triggered by page load, return current state
    if not ctx.triggered:
        return True, table_data

    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if triggered_id == "btn-reset":
        # Reset table
        reset_data = get_categories_table(df).to_dicts()
        return True, reset_data

    # Only validate if triggered by table data changes
    if triggered_id == "input-table":
        # Enable "Calculate exposure" only if at least one row has Use level > 0
        enable_calculate = any(
            row.get("Use level (mg/kg)") is not None and row.get("Use level (mg/kg)") > 0
            for row in table_data
        )

        # Clear "Consumers of" if Use level <= 0
        for row in table_data:
            if row.get("Use level (mg/kg)") is None or row.get("Use level (mg/kg)") <= 0:
                row["Consumers of"] = False

        return not enable_calculate, table_data

    # Default case
    return True, table_data


@callback(
    Output("btn-import", "n_clicks"),
    Input("btn-import", "n_clicks"),
    prevent_initial_call=True,
)
def import_placeholder(n):
    """Import input data from a file"""
    # Placeholder for future file upload logic
    return n

@callback(
    Output("btn-export", "n_clicks"),
    Input("btn-export", "n_clicks"),
    prevent_initial_call=True,
)
def export_placeholder(n):
    """Export input data to a file"""
    # Placeholder for future file export logic
    return n


@callback(
    Output("session-input-data", "data"),
    Output("results-tab", "disabled"),
    Output("navigation-trigger", "data"),
    Input("btn-calculate", "n_clicks"),
    State("input-table", "data"),
    prevent_initial_call=True,
)
def calculate_exposure(n_clicks, data):
    """Save input data to session storage and enable results tab.

    Args:
        n_clicks: Ignored
        data: The user input data
    """
    if n_clicks is None:
        raise dash.exceptions.PreventUpdate

    return data, False, "exposure-results"


@callback(
    Output("navigation-tabs", "value"),
    Input("navigation-trigger", "data"),
    prevent_initial_call=True,
)
def navigate_to_results(target_tab):
    """Navigate to the specified tab when triggered."""
    return target_tab


# ------------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
