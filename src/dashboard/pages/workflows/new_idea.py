import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

from src.dashboard.components.thesis_card import render_thesis_card

dash.register_page(__name__, path='/workflows/new-idea', name='New Idea Hunt')

layout = dbc.Container([
    html.H2("New Idea Hunt", className="mb-4"),
    html.P("Launch a new investment idea generation workflow.", className="text-muted"),
    
    html.Div([
        html.Div("Configuration", className="card-principal-header"),
        html.Div([
            dbc.Label("Investment Theme / Query"),
            dbc.Input(id="new-idea-input", placeholder="e.g., 'Find me a high quality compounder in the industrial sector'", type="text", className="mb-3"),
            dbc.Button("Launch Workflow", id="btn-launch-new-idea", color="success"),
        ], className="card-principal-body")
    ], className="card-principal mb-4"),
    
    html.Div([
        # Demo of the v0 Component
        # In a real run, this would be populated by the callback.
        # For now, we show the placeholder state or let the callback inject it.
        html.Div("Workflow Output", className="card-principal-header"),
        html.Div([
            dcc.Loading(
                id="loading-new-idea",
                type="default",
                children=html.Div(id="new-idea-output", children="Output will appear here...")
            )
        ], className="card-principal-body")
    ], className="card-principal")
])
