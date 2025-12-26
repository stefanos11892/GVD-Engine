import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/workflows/radar', name='News Radar')

layout = dbc.Container([
    html.H2("Portfolio News Radar", className="mb-4"),
    html.P("Scan for material events affecting your holdings.", className="text-muted"),
    
    html.Div([
        html.Div("Scan Settings", className="card-principal-header"),
        html.Div([
            dbc.Label("Focus Area"),
            dbc.Select(
                id="radar-focus",
                options=[
                    {"label": "All Holdings", "value": "all"},
                    {"label": "Watchlist Only", "value": "watchlist"},
                    {"label": "Macro Events", "value": "macro"},
                ],
                value="all",
                className="mb-3"
            ),
            dbc.Button("Scan News", id="btn-scan-radar", color="primary"),
        ], className="card-principal-body")
    ], className="card-principal mb-4"),
    
    html.Div([
        html.Div("Intelligence Feed", className="card-principal-header"),
        html.Div([
            dcc.Loading(
                id="loading-radar",
                type="default",
                children=html.Div(id="radar-output", children="News feed will appear here...")
            )
        ], className="card-principal-body")
    ], className="card-principal")
])
