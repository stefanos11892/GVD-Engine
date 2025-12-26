import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/strategy', name='Strategy Console')

layout = dbc.Container([
    html.H2("The Architect's Office", className="mb-4"),
    html.P("Configure the investment strategy, risk limits, and compliance rules.", className="text-muted"),
    
    dbc.Row([
        dbc.Col([
            html.Div([
                html.Div("Constitution & Mandate", className="card-principal-header"),
                html.Div([
                    dbc.Label("Investment Philosophy"),
                    dbc.Textarea(id="strategy-philosophy", placeholder="Define the core investment philosophy...", style={"height": "150px"}, className="mb-3"),
                    dbc.Label("Excluded Sectors"),
                    dbc.Input(id="strategy-excluded", placeholder="e.g., Tobacco, Gambling", type="text", className="mb-3"),
                    dbc.Button("Update Constitution", id="btn-update-constitution", color="primary"),
                ], className="card-principal-body")
            ], className="card-principal h-100")
        ], width=6),
        
        dbc.Col([
            html.Div([
                html.Div("Risk Parameters", className="card-principal-header"),
                html.Div([
                    dbc.Label("Max Allocation per Position (%)"),
                    dbc.Input(id="risk-max-alloc", type="number", value=10, className="mb-3"),
                    dbc.Label("Max Sector Exposure (%)"),
                    dbc.Input(id="risk-max-sector", type="number", value=25, className="mb-3"),
                    dbc.Label("Min Market Cap ($B)"),
                    dbc.Input(id="risk-min-cap", type="number", value=5, className="mb-3"),
                    dbc.Button("Save Parameters", id="btn-save-risk", color="warning"),
                ], className="card-principal-body")
            ], className="card-principal h-100")
        ], width=6),
    ])
])
