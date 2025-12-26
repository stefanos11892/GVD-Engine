import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/workflows/risk', name='Risk Report')

layout = dbc.Container([
    html.H2("Risk Management Report", className="mb-4"),
    html.P("Generate portfolio stress tests and risk metrics.", className="text-muted"),
    
    html.Div([
        html.Div("Risk Parameters", className="card-principal-header"),
        html.Div([
            dbc.Label("Target Assets"),
            dbc.Select(
                id="risk-target",
                options=[
                    {"label": "Whole Portfolio", "value": "portfolio"},
                    {"label": "Top 5 Holdings", "value": "top_5"},
                    {"label": "Technology Sector", "value": "tech"},
                ],
                value="portfolio",
                className="mb-3"
            ),
            dbc.Label("Stress Scenario"),
            dbc.Select(
                id="risk-scenario",
                options=[
                    {"label": "Market Crash (-20%)", "value": "crash_20"},
                    {"label": "Inflation Spike", "value": "inflation"},
                    {"label": "Sector Rotation", "value": "rotation"},
                ],
                value="crash_20",
                className="mb-3"
            ),
            dbc.Button("Run Stress Test", id="btn-run-risk", color="danger"),
        ], className="card-principal-body")
    ], className="card-principal mb-4"),
    
    html.Div([
        html.Div("Risk Analysis", className="card-principal-header"),
        html.Div([
            dcc.Loading(
                id="loading-risk",
                type="default",
                children=html.Div(id="risk-output", children="Risk metrics will appear here...")
            )
        ], className="card-principal-body")
    ], className="card-principal")
])
