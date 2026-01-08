"""
The Exposure Summary pane layout.
"""
from dash import html

__all__ = ["layout"]


def layout(session_data: list[dict]) -> html.Div:
    """Exposure summary page layout."""
    return html.Div(
        [
            html.H3("Exposure Summary"),
            html.P(
                "This section provides a summary of the exposure assessment results. "
                "Detailed results and graphs can be found in the respective tabs."
            ),
        ]
    )
