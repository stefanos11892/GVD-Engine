import dash_bootstrap_components as dbc
from dash import html

def create_sidebar():
    return dbc.Col([
        html.H4("GVD Engine", className="brand-logo mb-4"),
        html.Hr(),
        dbc.Nav([
            dbc.NavLink([html.I(className="bi bi-house-door me-2"), "Command Center"], href="/", active="exact"),
            dbc.NavLink([html.I(className="bi bi-graph-up me-2"), "Portfolio"], href="/portfolio", active="exact"),
            dbc.NavLink([html.I(className="bi bi-file-earmark-text me-2"), "Intelligence"], href="/intelligence", active="exact"),
        ], vertical=True, pills=True, className="bg-dark text-light p-2 rounded"),
        html.Hr(),
        html.H6("Workflows", className="text-muted ms-2"),
        dbc.Nav([
            dbc.NavLink([html.I(className="bi bi-lightbulb me-2"), "New Idea"], href="/workflows/new-idea", active="exact"),
            dbc.NavLink([html.I(className="bi bi-bar-chart-steps me-2"), "Earnings"], href="/workflows/earnings", active="exact"),
            dbc.NavLink([html.I(className="bi bi-calculator me-2"), "Forecasting"], href="/workflows/forecasting", active="exact"),
            dbc.NavLink([html.I(className="bi bi-shield-exclamation me-2"), "Risk Report"], href="/workflows/risk", active="exact"),
            dbc.NavLink([html.I(className="bi bi-broadcast me-2"), "Radar"], href="/workflows/radar", active="exact"),
            dbc.NavLink([html.I(className="bi bi-search me-2"), "Deep Dive"], href="/workflows/fundamental", active="exact"),
        ], vertical=True, pills=True, className="bg-dark text-light p-2 rounded"),
        html.Hr(),
        html.H6("Strategy", className="text-muted ms-2"),
        dbc.Nav([
            dbc.NavLink([html.I(className="bi bi-bank me-2"), "Architect's Office"], href="/strategy", active="exact"),
        ], vertical=True, pills=True, className="bg-dark text-light p-2 rounded"),
        html.Hr(),
        html.Div([
            html.Small("System Status:", className="text-muted"),
            html.Div([html.I(className="bi bi-circle-fill text-success me-2"), "Online"], className="text-success mt-1")
        ])
    ], width=2, className="sidebar p-4 vh-100 position-fixed")
