import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/workflows/fundamental', name='Deep Dive Analysis')

layout = dbc.Container([
    html.H2("Fundamental Deep Dive", className="mb-4"),
    html.P("Conduct comprehensive due diligence on a specific ticker.", className="text-muted"),
    
    html.Div([
        html.Div("Target Company", className="card-principal-header"),
        html.Div([
            dbc.Label("Ticker Symbol"),
            dbc.Input(id="fundamental-ticker", placeholder="e.g., MSFT", type="text", className="mb-3"),
            dbc.Button("Start Analysis", id="btn-start-analysis", color="info"),
        ], className="card-principal-body")
    ], className="card-principal mb-4"),
    
    html.Div([
        html.Div("Analyst Report", className="card-principal-header"),
        html.Div([
            dcc.Loading(
                id="loading-fundamental",
                type="default",
                children=html.Div(id="fundamental-output", children="Report will appear here...")
            )
        ], className="card-principal-body")
    ], className="card-principal")
])
