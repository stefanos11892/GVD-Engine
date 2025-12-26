import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import sys
import os

# Add project root to path to access agents
sys.path.append(os.path.join(os.getcwd(), "GVD_Engine"))

dash.register_page(__name__, path='/', name='Command Center')

def create_workflow_card(title, description, icon, link, color="secondary"):
    return html.Div([
        html.Div([
            html.Div([
                html.I(className=f"bi {icon} display-6 mb-3", style={"color": "var(--accent-primary)"}),
                html.H5(title, className="card-title fw-bold text-white"),
                html.P(description, className="card-text text-secondary small"),
            ], className="text-center"),
            html.Div([
                dbc.Button("Launch", href=link, color="primary", className="w-100 mt-3 btn-launch")
            ])
        ], className="card-principal-body")
    ], className="card-principal h-100 shadow-lg")

layout = dbc.Container([
    html.H2("Welcome to GVD Engine", className="mb-4 display-6 fw-bold"),
    html.P("Select a workflow to begin.", className="text-muted mb-5 lead"),
    
    # --- Row 1: Core Workflows ---
    html.H5("Start New", className="mb-4 text-white fw-medium"), # Scaled up, medium weight
    dbc.Row([
        dbc.Col(create_workflow_card("New Idea Hunt", "Originator Agent: Scan markets for new opportunities.", "bi-lightbulb", "/workflows/new-idea"), width=4, className="mb-4"),
        dbc.Col(create_workflow_card("Earnings Season", "Evaluator Agent: Analyze 10-Ks and transcripts.", "bi-bar-chart-steps", "/workflows/earnings"), width=4, className="mb-4"),
        dbc.Col(create_workflow_card("Deep Dive", "Analyst Agent: Fundamental due diligence.", "bi-search", "/workflows/fundamental"), width=4, className="mb-4"),
    ], className="g-4"), # Added Grid Gap
    
    # --- Row 2: Risk & Monitoring ---
    dbc.Row([
        dbc.Col(create_workflow_card("Risk Report", "Risk Office: Stress test the portfolio.", "bi-shield-exclamation", "/workflows/risk"), width=4, className="mb-4"),
        dbc.Col(create_workflow_card("News Radar", "Radar Agent: Scan for material events.", "bi-broadcast", "/workflows/radar"), width=4, className="mb-4"),
        dbc.Col(create_workflow_card("Forecasting", "Forecaster Agent: Financial modeling.", "bi-calculator", "/workflows/forecasting"), width=4, className="mb-4"),
    ], className="g-4"), # Added Grid Gap
    
    html.Hr(className="my-5 opacity-25"),
    
    # --- Section 3: Agent Chat (Bottom) ---
    html.H5("Quick Agent Access", className="text-muted mb-3 fw-medium"),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div(id="chat-history", style={"height": "120px", "overflow-y": "auto", "padding": "10px", "margin-bottom": "10px"}, className="small text-secondary"),
                    dbc.InputGroup([
                        dbc.Input(id="user-input", placeholder="Ask any agent directly...", type="text", className="rounded-pill me-2"),
                        dbc.Button("Send", id="send-btn", color="primary", className="rounded-pill px-4"),
                    ])
                ], className="p-3")
            ], className="border-0 bg-transparent") # Minimal container
        ], width=8, className="offset-2") # Centered and smaller
    ])
])

# Callback for chat interaction (Placeholder logic for now)
@callback(
    Output("chat-history", "children"),
    Input("send-btn", "n_clicks"),
    State("user-input", "value"),
    State("chat-history", "children"),
    prevent_initial_call=True
)
def update_chat(n_clicks, user_input, history):
    if not history:
        history = []
    
    # Append user message
    history.append(html.Div([html.B("You: "), user_input], className="text-info mb-2"))
    
    # Placeholder response
    history.append(html.Div([html.B("System: "), "Agent logic not yet connected to UI."], className="text-success mb-2"))
    
    return history
