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
import re
import logging

logger = logging.getLogger("AgentCallbacks")

def safe_json_parse(raw_str: str) -> dict:
    """Safely extract and parse JSON from LLM response strings."""
    if not raw_str:
        return {}
    try:
        # Remove markdown code fences
        clean = raw_str.replace("```json", "").replace("```", "").strip()
        # Regex to find outermost JSON object
        match = re.search(r'\{[\s\S]*\}', clean)
        if match:
            return json.loads(match.group(0))
        return {}
    except Exception as e:
        logger.warning(f"JSON parse failed: {e}")
        return {}

def render_rich_workflow_ui(data):
    """Parses agent JSONs and constructs a dashboard-like view."""
    try:
        # Extract & Parse with robust helper
        analyst_data = safe_json_parse(data.get("analyst", "{}"))
        risk_data = safe_json_parse(data.get("risk", "{}"))
        arch_data = safe_json_parse(data.get("architect", "{}"))
        
        # 1. Header (Architect Verdict)
        verdict = arch_data.get("decision", "HOLD")
        
        # Extract ticker - Try multiple sources
        ticker = arch_data.get("ticker", "")
        
        # Fallback 1: Extract from originator text (bold markdown pattern: **TICKER**)
        if not ticker or ticker == "???":
            import re
            raw_narrative = data.get("originator", "")
            # Match patterns like "**BRK.B**" or "**NVDA**"
            ticker_match = re.search(r'\*\*([A-Z]{1,5}(?:\.[A-Z])?)\*\*', raw_narrative)
            if ticker_match:
                ticker = ticker_match.group(1)
        
        # Fallback 2: Look in analyst_data
        if not ticker or ticker == "???":
            ticker = analyst_data.get("ticker", "???")
        
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

        # 2. Originator Text (Thesis) -> v0 Component
        from src.dashboard.components.thesis_card import render_thesis_card
        
        
        # 3. Analyst Stats (Move extraction up for usage)
        scores = analyst_data.get("scores", {})
        
        # Prepare Data for v0 Card
        card_status = verdict 
        if card_status not in ["PASS", "FAIL", "HOLD", "BUY", "SELL"]:
            card_status = "HOLD"
            
        # Parse deals from logic
        
        # Helper to clean narrative
        import re
        raw_narrative = data.get("originator", "Generating investment thesis...")
        # 1. Strip Markdown Table (lines starting with |)
        clean_narrative = re.sub(r'\|.*\|', '', raw_narrative).strip()
        # 2. Fix multiple newlines
        clean_narrative = re.sub(r'\n{3,}', '\n\n', clean_narrative)
        
        deal_data = {
            "ticker": ticker,
            "market_cap": "N/A",
            "pe": "N/A",
            "thesis": "" # Prevent duplication. Main narrative is at the top.
        }

        
        # Try to enrich with Analyst data first
        if scores:
             # If analyst provides explicit fields
             if "market_cap" in analyst_data: deal_data["market_cap"] = analyst_data.get("market_cap")
             if "pe_ratio" in analyst_data: deal_data["pe"] = str(analyst_data.get("pe_ratio"))
        
        # Fallback: Scrape Originator Table if metrics missing
        if deal_data["market_cap"] == "N/A" and ticker != "???":
            try:
                table_match = re.search(fr'\|\s*\**{re.escape(ticker)}\**\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|', raw_narrative, re.IGNORECASE)
                if table_match:
                    deal_data["market_cap"] = table_match.group(1).strip()
                    deal_data["pe"] = table_match.group(2).strip()
            except:
                pass
                
        # --- VALIDATION LAYER ---
        # Fetch real market data ONLY if we have a valid ticker
        from src.tools.market_data import get_market_data
        
        if ticker and ticker != "???" and len(ticker) <= 5:
            try:
                real_data = get_market_data(ticker)
                if real_data.get("pe"):
                    deal_data["pe"] = f"{real_data['pe']:.2f}"
                if real_data.get("market_cap"):
                    deal_data["market_cap"] = real_data["market_cap"]
            except Exception as e:
                logger.warning(f"Market data fetch failed for {ticker}: {e}")

        # The 'narrative' argument in v0 component matches 'originator' text
        # The 'deal_memo' argument matches the struct above
        
        originator_sec = render_thesis_card(
            ticker=ticker,
            status=card_status,
            narrative=clean_narrative,
            deal_memo=deal_data
        )

        # 3. Analyst Stats
        scores = analyst_data.get("scores", {})
        rationales = analyst_data.get("score_rationale", {})
        
        def render_neon_bar(label, value, key, color="info"):
            # Fix scaling: If value > 10, assume it's out of 100.
            # We want display out of 10.
            # We want width out of 100%.
            
            raw_val = value
            if raw_val > 10:
                display_val = raw_val / 10.0 # 95 -> 9.5
                width_val = raw_val # 95%
            else:
                display_val = raw_val # 9.5 -> 9.5
                width_val = raw_val * 10 # 95%
                
            # Bootstrap colors: text-info = cyan, text-primary = blue.
            style_color = "#3b82f6" # primary
            if color == "success": style_color = "#22c55e"
            if color == "warning": style_color = "#eab308"
            
            rationale_text = rationales.get(key, "No specific rationale provided.")
            
            return html.Div([
                html.Div([
                     html.Span(label, className="text-label"),
                     html.Span(f"{display_val:.1f}/10", className="text-value float-end small")
                ], className="mb-1 clearfix"),
                html.Div([
                    html.Div(className="progress-neon-bar", style={"width": f"{width_val}%", "backgroundColor": style_color, "color": style_color})
                ], className="progress-neon-container mb-0"),
                html.Div(rationale_text, className="text-white-50 small mt-1 mb-3 fst-italic", style={"fontSize": "0.75rem"})
            ])

        analyst_card = html.Div([
            html.Div("Fundamental Analysis", className="card-principal-header"),
            html.Div([
                render_neon_bar("Business Quality", scores.get("quality", 0), "quality", "primary"),
                render_neon_bar("Valuation", scores.get("valuation", 0), "valuation", "success"),
                # render_neon_bar("Management", scores.get("management", 0), "management", "warning"),
                # html.Div(f"TARGET: {analyst_data.get('fair_value_range', 'N/A')}", className="mt-2 text-center text-label")
                render_neon_bar("Management", scores.get("management", 0), "management", "warning")
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
                    html.Div(risk_data.get('max_drawdown_rationale', ''), className="text-secondary small px-2 py-1 mb-2 fst-italic", style={"fontSize": "0.75rem"}),
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
