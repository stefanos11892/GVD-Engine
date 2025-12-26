import dash
from dash import html, dcc, callback, Input, Output, State, no_update
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import traceback

dash.register_page(__name__, path='/workflows/forecasting', name='Financial Forecasting')

import json
from src.agents.analyst import AnalystAgent


# --- Helper: Generate Synthetic Data for Charts ---

def create_projection_chart(years_list, prices_list):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=years_list, y=prices_list, mode='lines+markers', name='Implied Valuation', line=dict(color='#3b82f6', width=3)))
    fig.update_layout(
        template="plotly_dark",
        title=dict(text="Projected Valuation", font=dict(family="Inter", size=14, color="#94a3b8")),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=350,
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(showgrid=True, gridcolor='rgba(255, 255, 255, 0.05)', title=""),
        yaxis=dict(showgrid=True, gridcolor='rgba(255, 255, 255, 0.05)', title="")
    )
    return fig

# ... (Layout is unchanged) ...

# Duplicate callback removed.

layout = dbc.Container([
    dcc.Store(id="forecast-json-store"), # Store for Agent Data
    
    # Header
    html.Div([
        html.H2("Financial Forecaster", id="header-ticker", className="text-white mb-0 brand-logo", style={"fontSize": "1.5rem", "marginBottom": "0"}),
        html.P("Real-Time Market Data | Powered by Forecaster Agent", className="text-secondary small")
    ], className="mb-4 d-flex justify-content-between align-items-end"),
    
    # Input Section
    dbc.Row([
        dbc.Col([
             dbc.InputGroup([
                dbc.Input(id="forecasting-ticker", placeholder="Enter Ticker (e.g. NVDA)...", type="text", className="form-control"),
                dbc.Button("Analyze", id="btn-run-forecasting", color="primary", className="btn-launch"),
            ], className="mb-4"),
        ], width=4)
    ]),

    dcc.Loading(id="loading-forecast", type="dot", children=[
        dbc.Row([
            # --- LEFT COLUMN: CONTROLS ---
            dbc.Col([
                html.Div([
                    html.Div("Scenario Inputs", className="card-principal-header fw-bold"),
                    html.Div([
                        # Valuation Method Toggle
                        html.Label("Valuation Method", className="text-secondary small"),
                        dbc.RadioItems(
                            options=[
                                {"label": "P/E Multiples", "value": "pe"},
                                {"label": "DCF (Earnings)", "value": "dcf"},
                            ],
                            value="pe",
                            id="radio-method",
                            inline=True,
                            className="mb-3 text-white small",
                            inputClassName="btn-check",
                            labelClassName="btn btn-outline-primary btn-sm",
                            labelCheckedClassName="active"
                        ),

                        # Scenario Presets
                        dbc.Label("Quick Scenarios", className="text-secondary small"),
                        dbc.ButtonGroup([
                            dbc.Button("Bear", id="btn-scen-bear", color="danger", outline=True, size="sm"),
                            dbc.Button("Base", id="btn-scen-base", color="secondary", outline=True, active=True, size="sm"),
                            dbc.Button("Bull", id="btn-scen-bull", color="success", outline=True, size="sm"),
                        ], className="d-flex w-100 mb-4"),
                    
                        html.Label("Revenue Growth (CAGR)", className="text-secondary small"),
                        dcc.Slider(0, 0.5, 0.01, value=0.15, marks=None, tooltip={"placement": "bottom", "always_visible": True}, id='slider-growth'),
                        
                        html.Label("PEG Factor (Target P/E = Growth × PEG)", className="text-secondary small mt-3"),
                        dcc.Slider(0.5, 3.0, 0.1, value=1.5, marks=None, tooltip={"placement": "bottom", "always_visible": True}, id='slider-peg'),

                        html.Div([
                            html.Label("Target Net Margin", className="text-secondary small mt-3"),
                            dcc.Slider(0, 0.6, 0.01, value=0.20, marks=None, tooltip={"placement": "bottom", "always_visible": True}, id='slider-margin'),
                            
                            html.Label("Target P/E Ratio (Manual Override)", className="text-secondary small mt-3"),
                            dcc.Slider(5, 100, 1, value=25, marks=None, tooltip={"placement": "bottom", "always_visible": True}, id='slider-pe'),
                        ], id="manual-inputs-container"), 
                        
                        html.Label("Annual Volatility (σ)", className="text-secondary small mt-3"),
                        dcc.Slider(0.1, 1.0, 0.01, value=0.35, marks=None, tooltip={"placement": "bottom", "always_visible": True}, id='slider-vol'),
                        
                        html.Hr(className="border-secondary my-4"),
                        
                        html.Div(id="baseline-metrics-container")
                    ], className="card-principal-body")
                ], className="card-principal h-100")
            ], width=3),
            
            # --- RIGHT COLUMN: CHARTS ---
            dbc.Col([
                # Top: Projection
                # Top: Projection
                html.Div([
                    html.Div([
                        dcc.Graph(id='graph-projection', config={'displayModeBar': False})
                    ], className="card-principal-body p-0")
                ], className="card-principal mb-4"),
                
                # Middle: Table
                html.Div([
                    html.Div("Pro Forma Income Statement & Valuation", className="card-principal-header"),
                    html.Div(id="pro-forma-table", className="card-principal-body p-0")
                ], className="card-principal mb-4"),
                
                # Bottom: Monte Carlo
                html.Div([
                    html.Div([
                        dcc.Graph(id='graph-monte-carlo', config={'displayModeBar': False}),
                        html.Div(id="mc-stats-container", className="p-3 border-top border-secondary")
                    ], className="card-principal-body p-0")
                ], className="card-principal")
                
            ], width=9)
        ])
    ]),

    # --- AI ANALYST REPORT SECTION (NEW) ---
    dbc.Row([
        dbc.Col([
            html.Div([
                html.Div([
                    html.Div("🤖 AI Investment Memo", className="fw-bold d-inline-block me-3"),
                    dbc.Button("Generate Deep Dive", id="btn-gen-ai-report", color="primary", size="sm", className="ms-auto", n_clicks=0)
                ], className="card-principal-header d-flex justify-content-between align-items-center"),
                html.Div([
                    dcc.Loading(id="loading-ai-report", type="cube", children=[
                        html.Div(id="ai-report-content", className="text-white")
                    ])
                ], className="card-principal-body")
            ], className="card-principal mb-5 shadow-lg")
        ], width=12)
    ], className="mt-4")

], fluid=True)

# --- Callbacks ---

# 1. Agent Call -> Store Data
@callback(
    Output("forecast-json-store", "data"),
    Input("btn-run-forecasting", "n_clicks"),
    State("forecasting-ticker", "value"),
    prevent_initial_call=True
)
def fetch_agent_data(n_clicks, ticker_input):
    if not ticker_input:
        return no_update
        
    ticker = ticker_input.strip().upper().replace(".", "")
    print(f"DEBUG: Dashboard fetching data for {ticker}...")
    
    # --- ARCHITECTURE REWRITE: DIRECT DATA FETCH ---
    # Bypass Agent Chain for now. Go straight to the source.
    from src.tools.market_data import get_market_data
    import json
    
    try:
        real_data = get_market_data(ticker)
        
        # SMART DEFAULTS CALCULATION
        # 1. PE Ratio
        price = real_data.get("price") or 100.0
        eps_raw = real_data.get("eps")
        try:
            eps = float(eps_raw) if eps_raw else None
        except:
            eps = None
            
        if eps and eps > 0:
            smart_pe = price / eps
            # Clamp for UI sanity (sliders usually go up to 100)
            if smart_pe > 100: smart_pe = 100
        else:
            smart_pe = 25.0
            
        # 2. Net Margin
        rev = real_data.get("revenue_ttm")
        net = real_data.get("net_income_ttm")
        if rev and net and rev > 0:
            smart_margin = net / rev
        else:
            smart_margin = 0.20
            
        # 3. Growth (Heuristic)
        # We don't have historical growth in this specific dict yet, 
        # so we default to a generally optimistic but realistic 15%.
        # In a future iteration we could scrape 'growth' specifically.
        smart_growth = 0.15

        # Build JSON manually
        final_data = {
            "ticker": ticker,
            "current_price": price,
            "eps": eps,
            "market_cap": real_data.get("market_cap"),
            "cash": real_data.get("cash", 0),
            "debt": real_data.get("debt", 0),
            "shares": real_data.get("shares"),
            "metrics": {
                "revenue": rev,
                "net_income": net
            },
            "base_case": {
                "volatility": real_data.get("volatility") or 0.35,
                # Use our calculated smart defaults
                "revenue_growth": smart_growth,
                "target_net_margin": smart_margin,
                "target_pe": smart_pe
            },
            "rationale": f"Smart Defaults: P/E set to {smart_pe:.1f} (capped), Margin to {smart_margin*100:.1f}% based on TTM data."
        }
        
        # Determine Rationale via Agent (Optional - skipped for speed/reliability)
        # If we wanted to, we could run the chain in a background thread or just omit it for now
        # to ensure the USER SEES DATA.
        
        return final_data

    except Exception as e:
        print(f"ERROR: Direct fetch failed: {e}")
        return None

# 2. Merged Callback: Manage UI State (Data Load + Scenarios)
@callback(
    [Output("header-ticker", "children"),
     Output("slider-growth", "value"),
     Output("slider-margin", "value"),
     Output("slider-pe", "value"),
     Output("slider-vol", "value"),
     Output("baseline-metrics-container", "children")],
    [Input("forecast-json-store", "data"),
     Input("btn-scen-bear", "n_clicks"),
     Input("btn-scen-base", "n_clicks"),
     Input("btn-scen-bull", "n_clicks")],
    [State("slider-growth", "value"),
     State("slider-margin", "value"),
     State("slider-pe", "value"),
     State("slider-vol", "value")]
)
def manage_ui_state(data, bear_c, base_c, bull_c, cg, cm, cp, cv):
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

    # Case A: Scenarios Clicked (Update Sliders Only)
    if trigger_id in ["btn-scen-bear", "btn-scen-base", "btn-scen-bull"]:
        # Allow Header/Metrics to stay same (no_update)
        if trigger_id == "btn-scen-bear":
            return no_update, 0.05, 0.10, 15, 0.45, no_update
        elif trigger_id == "btn-scen-bull":
            return no_update, 0.25, 0.25, 40, 0.30, no_update
        else: # Base
            return no_update, 0.15, 0.20, 25, 0.35, no_update

    # Case B: Data Loaded (Update Everything with Defaults)
    # This runs on initial load or new search
    if not data:
        return "Financial Forecaster", 0.15, 0.20, 25, 0.35, html.Div("No Data")
        
    ticker = data.get("ticker", "Unknown")
    base_case = data.get("base_case", {})
    
    # Defaults from Data
    growth = base_case.get("revenue_growth", 0.15)
    margin = base_case.get("target_net_margin", 0.20)
    pe = base_case.get("target_pe", 25)
    vol = base_case.get("volatility", 0.35)
    
    # Baseline Metrics UI Construction
    metrics = data.get("metrics", {})
    rev = metrics.get("revenue", "N/A")
    net = metrics.get("net_income", "N/A")
    # New fields
    eps = data.get("eps", "N/A") 
    mcap = data.get("market_cap", "N/A")
    
    price = data.get("current_price", 0)
    
    def fmt_money(v):
        if not v or v == "N/A": return "N/A"
        try:
            val = float(v)
            if val >= 1e9: return f"{val/1e9:.2f}B"
            if val >= 1e6: return f"{val/1e6:.2f}M"
            return f"{val:,.0f}"
        except: return str(v)

    baseline_ui = html.Div([
        html.Span("Baseline Metrics (TTM)", className="text-muted small text-uppercase"),
        html.Div([
            html.Span("Revenue", className="text-secondary"),
            html.Span(fmt_money(rev), className="text-white fw-bold")
        ], className="d-flex justify-content-between mt-2 small"),
        html.Div([
            html.Span("Net Income", className="text-secondary"),
            html.Span(fmt_money(net), className="text-white fw-bold")
        ], className="d-flex justify-content-between mt-1 small"),
        html.Div([
            html.Span("EPS (Diluted)", className="text-secondary"),
            html.Span(f"{eps}", className="text-white fw-bold")
        ], className="d-flex justify-content-between mt-1 small"),
        html.Div([
             html.Span("Market Cap", className="text-secondary"),
             html.Span(f"{mcap}", className="text-white fw-bold")
         ], className="d-flex justify-content-between mt-1 small"),
         html.Hr(className="my-2 border-secondary"),
         html.Div([
            html.Span("Current Price", className="text-secondary"),
            html.Span(f"${price:.2f}" if isinstance(price, (int, float)) else "N/A", className="text-success fw-bold")
        ], className="d-flex justify-content-between mt-1 small"),
    ])

    return f"Financial Forecaster: {ticker}", growth, margin, pe, vol, baseline_ui

# 4. Sliders -> Update Charts (Live Calculation)
@callback(
    [Output("graph-projection", "figure"), 
     Output("graph-monte-carlo", "figure"),
     Output("pro-forma-table", "children"),
     Output("mc-stats-container", "children")],
    [Input("slider-growth", "value"), 
     Input("slider-margin", "value"), 
     Input("slider-pe", "value"), 
     Input("slider-vol", "value"),
     Input("slider-peg", "value"),
     Input("radio-method", "value"),
     Input("forecast-json-store", "data")]
)
def update_simulation(growth, margin, pe_override, vol, peg, method, data):
    import traceback
    try:
        if data is None: data = {}
        
        # Defaults
        default_price = 100.0
        default_rev = 1_000_000_000.0
        
        if not data: 
            current_price = default_price
            current_rev = default_rev
            current_eps = 1.0 # Default EPS
        else:
            # Safely get price
            price_val = data.get("current_price")
            if isinstance(price_val, (int, float)):
                 current_price = price_val
            else:
                 current_price = default_price

            # Safely get revenue
            try:
                 metrics = data.get("metrics", {})
                 if not metrics: metrics = {}
                 
                 rev_val = metrics.get("revenue")
                 if rev_val is not None:
                     try:
                         current_rev = float(rev_val)
                     except:
                         current_rev = default_rev
                 else:
                     current_rev = default_rev
            except:
                 current_rev = default_rev
            
            # Safely get EPS
            try:
                eps_val = data.get("eps")
                if eps_val:
                    current_eps = float(eps_val)
                else:
                    current_eps = None
            except:
                current_eps = None

        # --- ARCHITECTURAL REFACTOR (PHASE 1) ---
        from src.logic.valuation import ValuationEngine

        # Determine Target PE based on Method (Restored)
        # Fix: Prioritize Manual Override Slider. 
        # Previously, 'pe' mode forced PEG calculation, ignoring the slider.
        # Now we trust the manual slider input.
        target_pe = pe_override
        
        # if method == "pe":
        #    target_pe = (growth * 100) * peg

        
        # Calculate Deterministic Valuation
        val_results = ValuationEngine.calculate_valuation(
            data.get("ticker", "UNKNOWN"), current_price, current_eps, current_rev, 
            growth, margin, target_pe, vol, peg, method, data
        )
        
        # Unpack Results
        proj_years = val_results["proj_years"]
        proj_prices = val_results["proj_prices"]
        implied_drift = val_results["implied_drift"]
        r_implied = val_results["r_implied"]
        
        # Reconstruct Table
        def fmt_b(v):
            if v >= 1e9: return f"{v/1e9:.2f}B"
            if v >= 1e6: return f"{v/1e6:.2f}M"
            return f"{v:,.0f}"
            
        rows = []
        for row in val_results["table_data"]:
            rows.append(html.Tr([
                html.Td(f"{row['year']} (E)"),
                html.Td(fmt_b(row['revenue'])),
                html.Td(f"+{int(row['growth_pct']*100)}%", className="text-success"),
                html.Td(fmt_b(row['net_income'])),
                html.Td(f"${row['eps']:.2f}" if row['eps'] else "-"), 
                html.Td(f"${row['price']:.2f} ({int(row['pe'])}x)", className="text-end fw-bold text-info")
            ]))
            
        table = html.Table([
            html.Thead([html.Tr([html.Th("Year"), html.Th("Revenue"), html.Th("Growth"), html.Th("Net Income"), html.Th("EPS"), html.Th("Implied Price (P/E)", className="text-end")])]),
            html.Tbody(rows)
        ], className="table table-dark table-hover table-sm mb-0 small", style={"background": "transparent"})

        # --- 3. Create Charts ---
        fig_proj = create_projection_chart(proj_years, proj_prices)
        
        # Monte Carlo (Vectorized)
        safe_vol = vol if vol else 0.35
        # GBM Correction: Median = S0 * exp(expected_drift * t)
        # Standard GBM Median includes (-0.5*sigma^2) drag.
        # We add it back to 'mu' so the output Median aligns with our Drift target.
        mu_adj = implied_drift + 0.5 * safe_vol**2
        
        paths = ValuationEngine.generate_monte_carlo(current_price, safe_vol, mu=mu_adj, simulations=2000)

        fig_mc = go.Figure()
        # Draw 50 paths
        for i in range(min(50, paths.shape[1])):
            fig_mc.add_trace(go.Scatter(y=paths[:, i], mode='lines', line=dict(color='rgba(59, 130, 246, 0.05)', width=1), showlegend=False))
            
        # Add Mean Path (Solid White Line - Visual Anchor)
        mean_path = np.mean(paths, axis=1)
        fig_mc.add_trace(go.Scatter(y=mean_path, mode='lines', name='Monte Carlo Mean', line=dict(color='white', width=3)))
        
        fig_mc.update_layout(
            template="plotly_dark",
            title=dict(text=f"Monte Carlo: Implied Drift {int(implied_drift*100)}%", font=dict(family="Inter", size=14, color="#94a3b8")),
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)',
            height=300, 
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis=dict(showgrid=True, gridcolor='rgba(255, 255, 255, 0.05)'),
            yaxis=dict(showgrid=True, gridcolor='rgba(255, 255, 255, 0.05)')
        )
        
        # --- 4. Stats Calculation ---
        final_prices = paths[-1]
        p10 = np.percentile(final_prices, 10)
        p50 = np.percentile(final_prices, 50)
        p90 = np.percentile(final_prices, 90)
        
        stats_ui = dbc.Row([
            dbc.Col([
                html.Div("10th Percentile (Downside)", className="text-secondary small text-center"),
                html.Div(f"${p10:.0f}", className="text-danger fw-bold fs-4 text-center")
            ]),
            dbc.Col([
                html.Div("Median Outcome", className="text-secondary small text-center"),
                html.Div(f"${p50:.0f}", className="text-primary fw-bold fs-4 text-center")
            ]),
            dbc.Col([
                html.Div("90th Percentile (Upside)", className="text-secondary small text-center"),
                html.Div(f"${p90:.0f}", className="text-success fw-bold fs-4 text-center")
            ])
        ])

        return fig_proj, fig_mc, table, stats_ui
        
    except Exception as e:
        print("CRITICAL ERROR in update_simulation:")
        traceback.print_exc()
        return go.Figure(), go.Figure(), html.Div(f"Error: {e}"), html.Div()

# 5. AI Analyst Report Callback (Async)
@callback(
    Output("ai-report-content", "children"),
    Input("btn-gen-ai-report", "n_clicks"),
    State("forecasting-ticker", "value"),
    State("forecast-json-store", "data"), # New: Access Dashboard Data
    prevent_initial_call=True
)
def generate_ai_report(n_clicks, ticker_input, dashboard_data):
    if not n_clicks or not ticker_input:
         return html.Div("Click 'Generate Deep Dive' to analyze.", className="text-muted text-center p-4")
         
    ticker = ticker_input.strip().upper()
    
    try:
        # Instantiate and Run Agent
        agent = AnalystAgent()
        # We wrap in a nice UI message while loading... actually dcc.Loading handles the spinner.
        
        # Run the agent (Time intensive: ~10-15s)
        # Pass rigid dashboard data to enforce consistency
        import json
        context_data = json.dumps(dashboard_data, indent=2) if dashboard_data else "No live dashboard data."
        
        prompt = f"Analyze {ticker}. STRICTLY use this dashboard data for valuation metrics: {context_data}"
        response_json_str = agent.run(prompt)
        
        # Parse JSON
        import re
        
        # Robust JSON Extraction
        json_str = response_json_str
        if "```json" in response_json_str:
             json_str = response_json_str.split("```json")[1].split("```")[0]
        elif "{" in response_json_str:
             start = response_json_str.find("{")
             end = response_json_str.rfind("}")
             json_str = response_json_str[start:end+1]
             
        data = json.loads(json_str)
        
        # UI Rendering
        rating = data.get("rating", "NEUTRAL")
        color_map = {"STRONG BUY": "success", "BUY": "success", "HOLD": "warning", "SELL": "danger", "SHORT": "danger"}
        rating_color = color_map.get(rating, "secondary")
        
        # Scores & Rationales
        scores = data.get("scores", {})
        rationales = data.get("score_rationale", {})
        
        return html.Div([
            # Top Row: Rating & Verdict
            dbc.Row([
                dbc.Col([
                    html.Div(rating, className=f"status-pill {rating.lower()} mb-2"),
                    html.Div(f"Fair Value: {data.get('fair_value_range', 'N/A')}", className="fs-5 text-white mt-1"),
                ], width=4, className="text-center border-fill border-end border-secondary p-4"),
                
                dbc.Col([
                    html.H5("Investment Verdict", className="text-info fw-bold"),
                    html.P(data.get("verdict_reasoning", "No verdict provided."), className="lead fs-6 text-light")
                ], width=8, className="ps-4")
            ], className="mb-4 align-items-center"),
            
            html.Hr(className="border-secondary"),
            
            # Middle Row: Scores & Methodology
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H6("Quality Score", className="text-muted text-uppercase small mb-1"),
                        dbc.Progress(value=scores.get("quality", 50), color="info", className="mb-1", style={"height": "8px"}),
                        html.P(rationales.get("quality", "Analysis pending..."), className="text-secondary small fst-italic mb-3")
                    ]),
                    
                    html.Div([
                        html.H6("Valuation Score", className="text-muted text-uppercase small mb-1"),
                        dbc.Progress(value=scores.get("valuation", 50), color="success", className="mb-1", style={"height": "8px"}),
                        html.P(rationales.get("valuation", "Analysis pending..."), className="text-secondary small fst-italic mb-3")
                    ]),
                    
                    html.Div([
                        html.H6("Management Score", className="text-muted text-uppercase small mb-1"),
                        dbc.Progress(value=scores.get("management", 50), color="warning", className="mb-1", style={"height": "8px"}),
                        html.P(rationales.get("management", "Analysis pending..."), className="text-secondary small fst-italic mb-0")
                    ]),
                ], width=5),
                
                dbc.Col([
                    html.H6("Forensic Methodology Checks", className="text-muted text-uppercase small mb-3"),
                    html.Ul([
                        html.Li([html.Span("ROIC vs WACC: ", className="fw-bold text-info"), data.get("methodology_check", {}).get("roic_vs_wacc", "N/A")]),
                        html.Li([html.Span("Earnings Quality: ", className="fw-bold text-info"), data.get("methodology_check", {}).get("earnings_quality", "N/A")]),
                        html.Li([html.Span("SBC Impact: ", className="fw-bold text-info"), data.get("methodology_check", {}).get("sbc_impact", "N/A")]),
                    ], className="list-unstyled text-small text-light mb-4"),
                    
                    html.Div([
                        html.H6("Detailed Analysis", className="text-muted text-uppercase small mb-2"),
                        html.P(data.get("detailed_analysis", "Generating deep dive analysis..."), className="text-white small", style={"lineHeight": "1.6", "textAlign": "justify", "fontSize": "0.9rem"})
                    ], className="p-3 bg-dark-glass border border-secondary rounded")
                    
                ], width=7)
            ], className="mb-4"),
            
            # Bottom Row: Bull/Bear
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("🐂 Bull Case", className="text-success fw-bold bg-dark-glass border-bottom border-success"),
                        dbc.CardBody(data.get("bull_case", "N/A"), className="text-white small")
                    ], className="border-success h-100 bg-transparent")
                ], width=6),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("🐻 Bear Case", className="text-danger fw-bold bg-dark-glass border-bottom border-danger"),
                        dbc.CardBody(data.get("bear_case", "N/A"), className="text-white small")
                    ], className="border-danger h-100 bg-transparent")
                ], width=6)
            ])
        ])
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return html.Div([
            html.H4("Analysis Failed", className="text-danger"),
            html.Pre(str(e), className="text-light small")
        ], className="p-3")
