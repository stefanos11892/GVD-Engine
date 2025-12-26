from dash import Input, Output, State, callback, html, dcc

import dash_bootstrap_components as dbc
import sys
import os
import time

# Ensure we can import from src
sys.path.append(os.path.join(os.getcwd(), "GVD_Engine"))

# Import actual Agents
from src.workflows.new_idea_chain import run_new_idea_chain
from src.workflows.earnings_season_chain import run_earnings_season_chain
from src.workflows.risk_chain import run_risk_chain
from src.workflows.radar_chain import run_radar_chain
from src.workflows.fundamental_chain import run_fundamental_chain
from src.workflows.forecasting_chain import run_forecasting_chain

import json

def render_rich_workflow_ui(data):
    """Parses agent JSONs and constructs a dashboard-like view."""
    try:
        # Extract & Parse
        analyst_data = json.loads(data.get("analyst", "{}").replace("```json", "").replace("```", "").strip())
        risk_data = json.loads(data.get("risk", "{}").replace("```json", "").replace("```", "").strip())
        arch_data = json.loads(data.get("architect", "{}").replace("```json", "").replace("```", "").strip())
        
        # 1. Header (Architect Verdict)
        verdict = arch_data.get("decision", "HOLD")
        ticker = arch_data.get("ticker", "???")
        
        # Verdict Logic: Dot Badge
        dot_color = "dot-green" if verdict in ["BUY"] else "dot-red" if verdict in ["SELL", "KILL"] else "dot-amber"
        # For PASS, we treat as Amber/Neutral or Green depending on context. User said green dot for PASS previously?
        # "Change PASS button to... transparent pill... tiny green dot" -> OK.
        if verdict == "PASS": 
            dot_color = "dot-green"
            
        header = dbc.Row([
            dbc.Col(html.H2(f"{ticker}", className="ticker-hero mb-0 ms-1"), width="auto"),
            dbc.Col(html.Div([
                html.Span("", className=f"dot {dot_color}"),
                html.Span(verdict)
            ], className="badge-status-dot ms-4"), width="auto")
        ], className="mb-4 align-items-center")

        # 2. Originator Text (Thesis)
        originator_sec = html.Div([
            html.Div("Investment Thesis", className="card-principal-header"),
            html.Div(
                dcc.Markdown(data.get("originator", "No thesis."), className="text-body-technical"),
                className="card-principal-body"
            )
        ], className="card-principal")

        # 3. Analyst Stats
        scores = analyst_data.get("scores", {})
        
        def render_neon_bar(label, value, color="info"):
            # color mapping for neon glow (handled by CSS currentcolor if possible, or classes)
            # Actually CSS sets shadow based on currentcolor. 
            # Bootstrap colors: text-info = cyan, text-primary = blue.
            style_color = "#3b82f6" # primary
            if color == "success": style_color = "#22c55e"
            if color == "warning": style_color = "#eab308"
            
            return html.Div([
                html.Div([
                     html.Span(label, className="text-label"),
                     html.Span(f"{int(value*10)}/10", className="text-value float-end small")
                ], className="mb-1 clearfix"),
                html.Div([
                    html.Div(className="progress-neon-bar", style={"width": f"{value*100}%", "backgroundColor": style_color, "color": style_color})
                ], className="progress-neon-container mb-4")
            ])

        analyst_card = html.Div([
            html.Div("Fundamental Analysis", className="card-principal-header"),
            html.Div([
                render_neon_bar("Business Quality", scores.get("quality", 0), "primary"),
                render_neon_bar("Valuation", scores.get("valuation", 0), "success"),
                render_neon_bar("Management", scores.get("management", 0), "warning"),
                html.Div(f"TARGET: {analyst_data.get('fair_value_range', 'N/A')}", className="mt-2 text-center text-label")
            ], className="card-principal-body")
        ], className="card-principal h-100")

        # 4. Risk Stats
        risk_rating = risk_data.get("risk_rating", "UNKNOWN")
        
        # Alert Banner Logic
        risk_banner = html.Div([
            html.Span("RISK LEVEL", className="text-label text-danger"),
            html.Span(risk_rating, className="alert-tag")
        ], className="alert-banner-risk")

        risk_card = html.Div([
            html.Div("Risk Assessment", className="card-principal-header"),
            html.Div([
                risk_banner,
                dbc.ListGroup([
                    dbc.ListGroupItem([
                         html.Span("MAX DRAWDOWN", className="text-label"),
                         html.Span(risk_data.get('max_drawdown_forecast', 'N/A'), className="float-end text-value")
                    ], className="bg-transparent border-bottom border-secondary p-2"),
                    dbc.ListGroupItem([
                         html.Span("BEAR CASE", className="text-label d-block mb-2 mt-2"),
                         html.Span(risk_data.get('scenarios', {}).get('market_crash_impact', 'N/A'), className="text-body-technical small")
                    ], className="bg-transparent border-0 p-0 mt-2")
                ], flush=True)
            ], className="card-principal-body")
        ], className="card-principal h-100")

        # 5. Architect Reason
        arch_card = html.Div([
            html.Div("Execution Strategy", className="card-principal-header"),
            html.Div(
                dcc.Markdown(arch_data.get("reasoning_summary", "No reasoning."), className="text-body-technical"), 
                className="card-principal-body"
            )
        ], className="card-principal")

        # Logs Accordion (Footer)
        logs_accordion = dbc.Accordion([
            dbc.AccordionItem(
                dcc.Markdown(data.get("logs", ""), className="terminal-output"),
                title="System Logs"
            )
        ], start_collapsed=True, className="mt-4 border-0")

        return html.Div([
            header, 
            dbc.Row([dbc.Col(originator_sec, width=12)]), # Full width thesis
            dbc.Row([dbc.Col(analyst_card, width=6), dbc.Col(risk_card, width=6)], className="mb-4"), 
            arch_card, 
            logs_accordion
        ], className="p-2")

    except Exception as e:
        # Fallback if parsing fails
        return html.Div([
            dbc.Alert(f"UI Build Failed: {e}", color="warning"),
            dcc.Markdown(data.get("logs", "No Logs"), className="terminal-output")
        ])

def execute_chain(chain_func, *args):
    try:
        output = chain_func(*args)
        if not output:
             return dbc.Alert("No output returned.", color="danger")
            
        # Check if Rich Data (Dict) or Legacy (String)
        if isinstance(output, dict):
            return render_rich_workflow_ui(output)
        
        # Legacy String
        return html.Div([
            dbc.Alert("Simple Output (Legacy)", color="info"),
            dcc.Markdown(str(output), className="terminal-output")
        ])
    except Exception as e:
        print(f"ERROR: {e}")
        return dbc.Alert(f"Error running workflow: {str(e)}", color="danger")

# --- New Idea Workflow Callback ---
@callback(
    Output("new-idea-output", "children"),
    Input("btn-launch-new-idea", "n_clicks"),
    State("new-idea-input", "value"),
    prevent_initial_call=True
)
def run_new_idea(n_clicks, user_input):
    if not user_input:
        return dbc.Alert("Please enter an investment theme.", color="warning")
    return execute_chain(run_new_idea_chain, user_input)

# --- Earnings Workflow Callback ---
@callback(
    Output("earnings-output", "children"),
    Input("btn-analyze-earnings", "n_clicks"),
    State("upload-data", "contents"), # Placeholder for file upload
    prevent_initial_call=True
)
def run_earnings(n_clicks, contents):
    # For now, we simulate a file path since upload logic is complex
    file_path = "Simulated_10K.pdf"
    return execute_chain(run_earnings_season_chain, file_path)

# --- Risk Workflow Callback ---
@callback(
    Output("risk-output", "children"),
    Input("btn-run-risk", "n_clicks"),
    State("risk-scenario", "value"),
    State("risk-target", "value"),
    prevent_initial_call=True
)
def run_risk_analysis(n_clicks, scenario, target):
    return execute_chain(run_risk_chain, scenario, target)

# --- Radar Workflow Callback ---
@callback(
    Output("radar-output", "children"),
    Input("btn-scan-radar", "n_clicks"),
    State("radar-focus", "value"),
    prevent_initial_call=True
)
def run_radar(n_clicks, focus):
    return execute_chain(run_radar_chain, focus)

# --- Fundamental Workflow Callback ---
@callback(
    Output("fundamental-output", "children"),
    Input("btn-start-analysis", "n_clicks"),
    State("fundamental-ticker", "value"),
    prevent_initial_call=True
)
def run_fundamental(n_clicks, ticker):
    if not ticker:
        return dbc.Alert("Please enter a ticker symbol.", color="warning")
    return execute_chain(run_fundamental_chain, ticker)

# --- Forecasting Workflow Callback ---
@callback(
    Output("forecast-output", "children"),
    Input("btn-generate-forecast", "n_clicks"),
    State("forecast-ticker", "value"),
    prevent_initial_call=True
)
def run_forecasting(n_clicks, ticker):
    if not ticker:
        return dbc.Alert("Please enter a ticker symbol.", color="warning")
    return execute_chain(run_forecasting_chain, ticker)
