import dash
from dash import html
import dash_bootstrap_components as dbc
import os

dash.register_page(__name__, name='Intelligence')

REPORTS_DIR = os.path.join(os.getcwd(), "GVD_Engine", "reports")

def list_reports():
    if not os.path.exists(REPORTS_DIR):
        return []
    return [f for f in os.listdir(REPORTS_DIR) if f.endswith(".md") or f.endswith(".pdf")]

layout = dbc.Container([
    html.H2("Intelligence Library", className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Generated Reports"),
                dbc.CardBody([
                    html.Ul([html.Li(f) for f in list_reports()]) if list_reports() else html.P("No reports found.")
                ])
            ])
        ])
    ])
])
