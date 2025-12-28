import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import logging
import json
import os
import plotly.graph_objects as go
from src.utils.pdf_renderer import PDFRenderer

# Register Page
dash.register_page(__name__, path='/earnings-workstation', name="Earnings Workstation")

logger = logging.getLogger("EarningsPage")

# --- DATA LOADER ---
def load_data():
    """Lengths for MVP: Load the JSON files generated in Phase 4."""
    report_path = "synthesis_report.json"
    log_path = "verification_log.json"
    
    report = {}
    if os.path.exists(report_path):
        with open(report_path, "r") as f:
            report = json.load(f)
            
    logs = {}
    if os.path.exists(log_path):
         with open(log_path, "r") as f:
            logs = json.load(f)
            
    return report, logs

report_data, log_data = load_data()
pdf_path = "complex_10k.pdf" # Default target for MVP

# --- LAYOUT ---
layout = dbc.Container([
    # Store Data Client-Side
    dcc.Store(id='report-store', data=report_data),
    dcc.Store(id='log-store', data=log_data),
    dcc.Store(id='pdf-page-store', data={'page': 1}), # Tracks current page
    
    dbc.Row([
        # --- LEFT PANEL: INVESTMENT MEMO ---
        dbc.Col([
            html.H4("Institutional Thesis", className="mb-3"),
            html.Div(id='thesis-container', className="p-3 border rounded", style={"height": "80vh", "overflowY": "scroll", "backgroundColor": "#121212", "color": "#FFFFFF", "borderColor": "#333"}),
        ], width=4),
        
        # --- RIGHT PANEL: PDF CANVAS ---
        dbc.Col([
            dbc.Row([
               dbc.Col([html.H4("Source Document Navigator")], width=8),
               dbc.Col([
                   dbc.Button("Prev", id="btn-prev", size="sm", className="me-2"),
                   html.Span(id="page-indicator", children="Page 1"),
                   dbc.Button("Next", id="btn-next", size="sm", className="ms-2"),
               ], width=4, className="text-end") 
            ], className="mb-2"),
            
            dcc.Graph(
                id='pdf-canvas',
                config={'displayModeBar': True, 'scrollZoom': True},
                style={"height": "75vh"}
            )
        ], width=5),
        
        # --- SIDEBAR: AUDIT TRAIL ---
        dbc.Col([
            html.H5("Adversarial Audit Panel", className="text-danger"),
            html.Hr(),
            html.Div(id='audit-panel-content', children=[
                html.P("Select a metric to view audit trail.", className="text-muted")
            ])
        ], width=3, className="border-start")
    ])
], fluid=True, className="p-4")

# --- CALLBACKS (Logic) ---
# Note: For strict MVC, callbacks should be in `src/dashboard/callbacks/`.
# However, for Dash Pages, inline callbacks or registering them in app.py is common.
# We will define the layout here and the Logic in `earnings_callbacks.py` as planned.
