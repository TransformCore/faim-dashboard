"""

"""
from dash import html

__all__ = ['exposure_summary', 'exposure_results', 'graph_average_exposure', 'graph_p975_exposure']


def exposure_summary() -> html.Div:
    return html.Div([
        html.H3('Exposure Summary'),
    ])


def exposure_results():
    return html.Div([
        html.H3('Exposure Results'),
    ])


def graph_average_exposure():
    return html.Div([
        html.H3('Average Exposure Graph'),
    ])


def graph_p975_exposure():
    return html.Div([
        html.H3('97.5th Percentile Exposure Graph'),
    ])
