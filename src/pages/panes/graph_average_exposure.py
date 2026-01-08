"""
The Average Exposure Graph pane layout.
"""
from dash import html

__all__ = ["layout"]


def layout(session_data: list[dict]) -> html.Div:
    """Graph Average Exposure page layout."""
    return html.Div(
        [
            html.H3("Graph Average Exposure"),
            html.P(
                "This section provides a summary of the exposure assessment results. "
                "Detailed results and graphs can be found in the respective tabs."
            ),
        ]
    )
