from dash import Input, Output, State, ALL, callback, html, dcc, ctx
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import json
import logging
import os
from src.utils.pdf_renderer import PDFRenderer

logger = logging.getLogger("EarningsCallbacks")

# Global renderer removed to prevent file handle leaks.
# Use get_cached_renderer(path) instead.

LOG_PATH = "verification_log.json"

def load_verification_log():
    """Safely load the verification log"""
    if not os.path.exists(LOG_PATH):
        return None
    try:
        with open(LOG_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load log: {e}")
        return None

# --- CALLBACK LOGIC (Top Level for Testing) ---

def render_memo_logic(report):
    # Prefer store data if available (Real-time update)
    log_data = report if report else load_verification_log()
    
    # Default text if no analysis runs
    if not log_data:
        return html.P("No Analysis Data Found. Please Run Workflow.", className="text-muted")

    # Dynamic Content from Log
    metrics = log_data.get('metrics', [])
    quant_note = log_data.get('quant_note') or log_data.get('quant_error')
    
    if not metrics and quant_note:
        return [
             html.H5("⚠️ Analysis Warning", className="text-warning"),
             html.P(quant_note, className="text-light bg-dark p-2 border border-warning rounded"),
             html.Small(f"Run ID: {log_data.get('run_id')}", className="text-muted")
        ]
    
    
    # --- STRATEGIC EVALUATION (Phase 5 - Berkshire Edition) ---
    thesis = log_data.get('institutional_thesis')
    
    header_elems = []
    if thesis:
        # Ensure thesis is a dict before proceeding - convert string to dict if needed
        if isinstance(thesis, str):
            # If thesis is a string, it's not parseable - show raw text
            thesis = {
                'final_verdict': 'NEUTRAL',
                'conviction_score': 0.5,
                'institutional_thesis': thesis[:200] + '...' if len(thesis) > 200 else thesis,
                'economic_reality': {'ocf_vs_net_income': 'N/A', 'owner_earnings_estimate': 'N/A', 'reasoning': ''},
                'capital_allocation': {'grade': 'N/A', 'retained_earnings_effectiveness': 'N/A', 'buyback_timing': 'N/A', 'reasoning': ''},
                'moat_margin': {'durability': 'N/A', 'operating_margin_trend': 'N/A', 'reasoning': ''},
                'narrative_integrity': {'multiplier': 1.0, 'findings': [], 'reasoning': ''},
                'key_risks': []
            }
        elif isinstance(thesis, dict):
            # Handle case where JSON parsing failed but raw markdown exists
            if 'error' in thesis and 'raw' in thesis:
                import re
                raw_text = thesis.get('raw', '')
                
                # Parse markdown for values
                def extract_value(pattern, text, default):
                    match = re.search(pattern, text, re.IGNORECASE)
                    return match.group(1) if match else default
                
                # Extract key values from markdown
                conviction_match = re.search(r'conviction score[:\s]*([0-9.]+)', raw_text, re.IGNORECASE)
                verdict_match = re.search(r'final verdict[:\s*\n]*\*?\*?([A-Z]+)', raw_text, re.IGNORECASE)
                thesis_type_match = re.search(r'\*\*(SOLID|TRANSITIONING|FRAGILE)\*\*', raw_text, re.IGNORECASE)
                
                # Economic Reality
                ocf_match = re.search(r'ocf_vs_net_income[^\|]*\|\s*([^\|]+)', raw_text, re.IGNORECASE)
                owner_earn_match = re.search(r'owner_earnings_estimate[^\|]*\|\s*([^\|]+)', raw_text, re.IGNORECASE)
                econ_reasoning_match = re.search(r'Economic Reality[^|]*reasoning[^\|]*\|\s*([^\|]+)', raw_text, re.IGNORECASE | re.DOTALL)
                
                # Capital Allocation
                cap_grade_match = re.search(r'Capital Allocation[^|]*grade[^\|]*\|\s*([^\|]+)', raw_text, re.IGNORECASE)
                retained_match = re.search(r'retained_earnings_effectiveness[^\|]*\|\s*([^\|]+)', raw_text, re.IGNORECASE)
                buyback_match = re.search(r'buyback_timing[^\|]*\|\s*([^\|]+)', raw_text, re.IGNORECASE)
                cap_reasoning_match = re.search(r'Capital Allocation[^|]*reasoning[^\|]*\|\s*([^\|]+)', raw_text, re.IGNORECASE | re.DOTALL)
                
                # Moat & Margin
                moat_match = re.search(r'durability[^\|]*\|\s*(Strong|Moderate|Weak)', raw_text, re.IGNORECASE)
                margin_trend_match = re.search(r'operating_margin_trend[^\|]*\|\s*([^\|]+)', raw_text, re.IGNORECASE)
                moat_reasoning_match = re.search(r'Moat.*Margin[^|]*reasoning[^\|]*\|\s*([^\|]+)', raw_text, re.IGNORECASE | re.DOTALL)
                
                # Narrative Integrity
                multiplier_match = re.search(r'multiplier[^\|]*\|\s*([0-9.]+)', raw_text, re.IGNORECASE)
                findings_match = re.findall(r'"([^"]+Omission[^"]+|[^"]+Retreat[^"]+)"', raw_text, re.IGNORECASE)
                narr_reasoning_match = re.search(r'Narrative Integrity[^|]*reasoning[^\|]*\|\s*([^\|]+)', raw_text, re.IGNORECASE | re.DOTALL)
                
                # Key Risks
                risks_matches = re.findall(r'\d+\.\s*\*\*([^:]+):\*\*\s*([^\n]+)', raw_text)
                
                # Build structured thesis from markdown
                thesis = {
                    'final_verdict': verdict_match.group(1) if verdict_match else 'HOLD',
                    'conviction_score': float(conviction_match.group(1)) if conviction_match else 0.5,
                    'institutional_thesis': thesis_type_match.group(1) if thesis_type_match else 'NEUTRAL',
                    'economic_reality': {
                        'weight': '50%',
                        'score': 0.9,
                        'ocf_vs_net_income': ocf_match.group(1).strip() if ocf_match else 'N/A',
                        'owner_earnings_estimate': owner_earn_match.group(1).strip() if owner_earn_match else 'N/A',
                        'reasoning': econ_reasoning_match.group(1).strip()[:500] if econ_reasoning_match else ''
                    },
                    'capital_allocation': {
                        'weight': '25%',
                        'grade': cap_grade_match.group(1).strip() if cap_grade_match else 'N/A',
                        'retained_earnings_effectiveness': retained_match.group(1).strip() if retained_match else 'N/A',
                        'buyback_timing': buyback_match.group(1).strip() if buyback_match else 'N/A',
                        'reasoning': cap_reasoning_match.group(1).strip()[:500] if cap_reasoning_match else ''
                    },
                    'moat_margin': {
                        'weight': '15%',
                        'durability': moat_match.group(1).strip() if moat_match else 'N/A',
                        'operating_margin_trend': margin_trend_match.group(1).strip() if margin_trend_match else 'N/A',
                        'reasoning': moat_reasoning_match.group(1).strip()[:500] if moat_reasoning_match else ''
                    },
                    'narrative_integrity': {
                        'weight': '10%',
                        'multiplier': float(multiplier_match.group(1)) if multiplier_match else 1.0,
                        'findings': findings_match or [],
                        'reasoning': narr_reasoning_match.group(1).strip()[:500] if narr_reasoning_match else ''
                    },
                    'key_risks': [f"{r[0]}: {r[1]}" for r in risks_matches] if risks_matches else []
                }
            
        verdict = thesis.get('final_verdict', 'NEUTRAL')
        score = thesis.get('conviction_score', 0)
        inst_thesis_statement = thesis.get('institutional_thesis', verdict)
        
        # NEW: Structured Berkshire Edition Fields
        econ_reality = thesis.get('economic_reality', {})
        capital_alloc = thesis.get('capital_allocation', {})
        moat_margin = thesis.get('moat_margin', {})
        narr_integrity = thesis.get('narrative_integrity', {})
        key_risks = thesis.get('key_risks', [])
        
        # Legacy fallback for old schema
        if not econ_reality and 'owner_earnings_analysis' in thesis:
            econ_reality = {
                'score': 0.5, 'ocf_vs_net_income': thesis.get('owner_earnings_analysis', {}).get('ocf_vs_net_income', 'N/A'),
                'owner_earnings_estimate': thesis.get('owner_earnings_analysis', {}).get('owner_earnings_estimate', 'N/A'),
                'reasoning': 'Legacy data - see details above'
            }
        
        try:
            # Color Logic
            score_val = float(score) if score is not None else 0.0
            score_color = "success" if score_val >= 0.8 else "warning" if score_val >= 0.5 else "danger"
            verdict_str = str(verdict) if verdict else "NEUTRAL"
            verdict_color = "success" if "buy" in verdict_str.lower() else "danger" if "sell" in verdict_str.lower() else "info"
            
            # Helper for section score color
            def section_color(val):
                try:
                    v = float(val)
                    return "success" if v >= 0.8 else "warning" if v >= 0.5 else "danger"
                except:
                    return "secondary"
            
            def grade_color(grade):
                return "success" if grade in ["A", "B"] else "warning" if grade == "C" else "danger"
            
            def moat_color(durability):
                return "success" if durability == "Strong" else "warning" if durability == "Moderate" else "danger"

            header_elems = [
                html.Div([
                    # --- HEADER ---
                    html.H3(f"{verdict_str.upper()}", className=f"text-{verdict_color} mb-0"),
                    html.H6(f"Conviction Score: {score_val:.2f}", className=f"text-{score_color}"),
                    dbc.Progress(value=score_val*100, color=score_color, className="mb-3", style={"height": "10px"}),
                    
                    # --- 1. ECONOMIC REALITY (50%) ---
                    html.Div([
                        html.H5([
                            dbc.Badge("50%", color="primary", className="me-2"),
                            "📊 Economic Reality (Owner Earnings)"
                        ], className="text-light mb-2"),
                        html.Ul([
                            html.Li(f"OCF vs Net Income: {econ_reality.get('ocf_vs_net_income', 'N/A')}", className="small text-info"),
                            html.Li(f"Owner Earnings Estimate: {econ_reality.get('owner_earnings_estimate', 'N/A')}", className="small text-info"),
                        ], className="mb-2"),
                        html.P(econ_reality.get('reasoning', ''), className="small text-light fst-italic border-start border-info ps-2 ms-2"),
                    ], className="mb-3 p-2 bg-dark rounded"),
                    
                    # --- 2. CAPITAL ALLOCATION (25%) ---
                    html.Div([
                        html.H5([
                            dbc.Badge("25%", color="info", className="me-2"),
                            "💰 Capital Allocation ",
                            dbc.Badge(capital_alloc.get('grade', 'N/A'), color=grade_color(capital_alloc.get('grade', 'N/A')), className="ms-2"),
                        ], className="text-light mb-2"),
                        html.Ul([
                            html.Li(f"Retained Earnings: {capital_alloc.get('retained_earnings_effectiveness', 'N/A')}", className="small text-info"),
                            html.Li(f"Buyback Timing: {capital_alloc.get('buyback_timing', 'N/A')}", className="small text-info"),
                        ], className="mb-2"),
                        html.P(capital_alloc.get('reasoning', ''), className="small text-light fst-italic border-start border-info ps-2 ms-2"),
                    ], className="mb-3 p-2 bg-dark rounded"),
                    
                    # --- 3. MOAT & MARGIN (15%) ---
                    html.Div([
                        html.H5([
                            dbc.Badge("15%", color="secondary", className="me-2"),
                            "🏰 Moat & Margin ",
                            dbc.Badge(moat_margin.get('durability', 'N/A'), color=moat_color(moat_margin.get('durability', 'N/A')), className="ms-2"),
                        ], className="text-light mb-2"),
                        html.P(f"Operating Margin Trend: {moat_margin.get('operating_margin_trend', 'N/A')}", className="small text-info mb-1"),
                        html.P(moat_margin.get('reasoning', ''), className="small text-light fst-italic border-start border-info ps-2 ms-2"),
                    ], className="mb-3 p-2 bg-dark rounded"),
                    
                    # --- 4. NARRATIVE INTEGRITY (10%) ---
                    html.Div([
                        html.H5([
                            dbc.Badge("10%", color="warning", className="me-2"),
                            "⚠️ Narrative Integrity ",
                            dbc.Badge(f"{narr_integrity.get('multiplier', 1.0):.2f}x", 
                                      color="success" if float(narr_integrity.get('multiplier', 1.0)) >= 1.0 else "danger", 
                                      className="ms-2"),
                        ], className="text-light mb-2"),
                        html.Ul([html.Li(f, className="small text-warning") for f in narr_integrity.get('findings', [])], className="mb-2") if narr_integrity.get('findings') else html.P("No integrity issues found.", className="small text-success"),
                        html.P(narr_integrity.get('reasoning', ''), className="small text-light fst-italic border-start border-warning ps-2 ms-2"),
                    ], className="mb-3 p-2 bg-dark rounded"),
                    
                    # --- KEY RISKS ---
                    html.Hr(className="border-secondary"),
                    html.H6("🚩 Key Risks", className="text-light"),
                    html.Ul([html.Li(r, className="small text-danger") for r in key_risks], className="mb-2") if key_risks else html.P("No significant risks identified.", className="small text-muted"),
                    
                ], className="mb-4 p-3 bg-opacity-10 bg-black border border-secondary rounded")
            ]
        except Exception as e:
            logger.error(f"Thesis Rendering Error: {e}")
            header_elems = [html.Div(f"Thesis Formatting Error: {e}", className="text-danger")]
        
    md_text = f"### Verification Detail\n**Run ID:** `{log_data.get('run_id')}`\n\n"
    
    friction_elems = []
    for i, m in enumerate(metrics):
        # Display Everything (Verified or Not)
        history = m.get('audit_history', [])
        verification = m.get('verification', {})
        
        # Icon Logic
        if verification.get('status') == 'error_detected':
            status_icon = "⚠️" 
            border_color = "border-warning"
            text_color = "text-warning"
        elif verification.get('status') == 'verified':
             status_icon = "✅"
             border_color = "border-success"
             text_color = "text-success"
        else:
             status_icon = "❓"
             border_color = "border-secondary" 
             text_color = "text-muted"

        metric_name = m.get('display_name')
        
        friction_elems.append(
            dbc.Button([
                html.H6(f"{status_icon} {metric_name}: {m.get('value_raw')}", className=f"{text_color} mb-1"),
                html.P(f"Adversarial Recovery Used: {m.get('recovery_used')}", className="small text-wrap text-muted")
            ], 
            id={'type': 'friction-item', 'index': i}, 
            color="dark", 
            outline=True, 
            className=f"mb-2 p-2 w-100 text-start {border_color}")
        )
        
    return header_elems + [dcc.Markdown(md_text, className="text-light")] + friction_elems


def update_pdf_view_logic(prev_n, next_n, friction_clicks, report_data, page_data):
    triggered = ctx.triggered_id
    
    # Priority: Use Report Data (New Job) -> Disk (Reload)
    log_data = report_data if report_data else load_verification_log()
    
    # Handle None page_data (Initial Load)
    page_data = page_data or {}
    current_page = page_data.get('page', 1)
    highlight_bbox = None
    
    # If triggered by Report Update (New Job Completed), Reset Page
    if triggered == 'report-store':
        current_page = 1
    
    # Dynamic Renderer
    # Use path from log if available, otherwise default
    pdf_path = log_data.get('pdf_path', 'complex_10k.pdf') if log_data else 'complex_10k.pdf'
    
    # Ensure PDF exists (handle uploads)
    renderer = get_cached_renderer(pdf_path)
    if not renderer:
         # Fallback or Error
         return go.Figure().update_layout(title="PDF Not Found"), "Error", {'page': 1}
    
    # Navigation Logic
    if triggered == 'btn-prev':
        current_page -= 1
    elif triggered == 'btn-next':
        current_page += 1
        
    # Jump Logic (Friction Click)
    elif isinstance(triggered, dict) and triggered.get('type') == 'friction-item':
        idx = triggered.get('index')
        if idx is not None and log_data and 0 <= idx < len(log_data.get('metrics', [])):
            metric = log_data['metrics'][idx]
            prov = metric.get('provenance', {})
            
            # Dynamic JUMP
            target_page = prov.get('page', 1)
            target_bbox = prov.get('bbox') 
            
            if target_page:
                current_page = target_page
            if target_bbox:
                highlight_bbox = target_bbox
        
    return generate_pdf_figure(current_page, renderer, highlight_bbox)


def update_audit_sidebar_logic(clicks):
    if not any(clicks):
        return html.P("Select a metric trace to view Auditor logic.", className="text-muted")
        
    triggered = ctx.triggered_id
    if not isinstance(triggered, dict):
            return html.P("Selection Error", className="text-danger")
            
    idx = triggered.get('index')
    log_data = load_verification_log()
    
    if not log_data or idx is None or idx >= len(log_data.get('metrics', [])):
        return html.P("Log data unavailable.", className="text-danger")
        
    metric = log_data['metrics'][idx]
    verification = metric.get('verification', {})
    history = metric.get('audit_history', [])
    
    status_color = "success" if verification.get('status') == 'verified' else "danger"
    
    # Build History Elements
    history_elems = []
    for h in history:
        history_elems.append(
            html.Div([
                html.Span(f"Attempt {h.get('attempt')}: ", className="text-muted"),
                html.Span(f"Value '{h.get('value_raw')}'", className="text-warning"),
                html.P(f"Note: {h.get('verification', {}).get('note')}", className="small text-danger fst-italic")
            ], className="mb-2 border-bottom border-secondary pb-1")
        )

    return html.Div([
        html.H6(f"Audit: {metric.get('display_name')}", className="text-white"),
        dbc.Badge(f"Status: {verification.get('status')}", color=status_color, className="mb-2"),
        
        html.H6("Auditor's Final Note", className="text-white mt-3"),
        html.P(verification.get('note'), className="small text-light bg-dark p-2 rounded"),
        
        html.Hr(className="border-secondary"),
        html.H6("Adversarial History", className="text-white"),
        html.Div(history_elems, className="small border p-2 rounded border-secondary")
    ])

# --- HELPER LOGIC (Testable) ---

# ======================================
# PDF RENDERER CACHING WITH CLEANUP
# ======================================
# Problem: lru_cache doesn't call close() on old renderers when path changes.
# Solution: Manual cache with explicit cleanup.

_renderer_cache = {"path": None, "instance": None}

def get_cached_renderer(pdf_path):
    """Returns a cached PDFRenderer, closing the old one if the path changed."""
    global _renderer_cache
    
    if not os.path.exists(pdf_path):
        return None
    
    # If path changed, close old renderer and create new one
    if _renderer_cache["path"] != pdf_path:
        if _renderer_cache["instance"] is not None:
            try:
                _renderer_cache["instance"].close()
                logger.info(f"Closed old renderer for: {_renderer_cache['path']}")
            except Exception as e:
                logger.warning(f"Error closing old renderer: {e}")
        
        _renderer_cache["instance"] = PDFRenderer(pdf_path)
        _renderer_cache["path"] = pdf_path
        logger.info(f"Created new renderer for: {pdf_path}")
    
    return _renderer_cache["instance"]

def generate_pdf_figure(current_page, renderer, highlight_bbox=None):
    """
    Standalone logic to generate the Plotly Figure for a PDF page.
    highlight_bbox: [x0, y0, x1, y1] in PDF Points (Bottom-Left Origin).
    """
    zoom_level = 2.0 
    total_pages = renderer.get_page_count()
    current_page = max(1, min(total_pages, current_page))
    
    # Get Image & Scale Factor (New API)
    # Returns: img_str, width, height, scale_factor
    img_str, width, height, scale_factor = renderer.get_page_image(current_page, zoom=zoom_level)
    
    # Create Figure
    fig = go.Figure()
    
    # Add Image as Background
    fig.add_layout_image(
        dict(
            source=img_str,
            xref="x", yref="y",
            x=0, y=height, # Image Top-Left at (0, height) implies Bottom-Left at (0,0)
            sizex=width,
            sizey=height,
            sizing="stretch",
            layer="below"
        )
    )
    
    # Set Axis Range (Matches Pixel Dimensions)
    fig.update_xaxes(range=[0, width], showgrid=False, zeroline=False, visible=False)
    fig.update_yaxes(range=[0, height], showgrid=False, zeroline=False, visible=False)
    
    fig.update_layout(
        width=None, 
        height=None, 
        margin=dict(l=0, r=0, t=0, b=0),
        dragmode="pan",
        plot_bgcolor="#121212", 
        paper_bgcolor="#121212"
    )
    
    # Draw BBox
    if highlight_bbox:
        pdf_x0, pdf_y0, pdf_x1, pdf_y1 = highlight_bbox
        
        # Apply DPI Scale Factor (Fix Coordinate Drift)
        # Docling (Bottom-Left) -> Plotly (Bottom-Left). No Y-flip needed.
        rect_x0 = pdf_x0 * scale_factor
        rect_x1 = pdf_x1 * scale_factor
        rect_y0 = pdf_y0 * scale_factor
        rect_y1 = pdf_y1 * scale_factor
        
        fig.add_shape(
            type="rect",
            x0=rect_x0, y0=rect_y0, 
            x1=rect_x1, y1=rect_y1, 
            line=dict(color="Red", width=3),
            fillcolor="rgba(255, 0, 0, 0.2)"
        )


    return fig, f"Page {current_page} of {total_pages}", {'page': current_page}


def register_earnings_callbacks(app):
    
    # --- 1. RENDER MEMO ---
    app.callback(
        Output('thesis-container', 'children'),
        Input('report-store', 'data')
    )(render_memo_logic) # Bind logic function

    # --- 2. UPDATE PDF VIEWER (JUMP & NAV) ---
    app.callback(
        [Output('pdf-canvas', 'figure'),
         Output('page-indicator', 'children'),
         Output('pdf-page-store', 'data')],
        [Input('btn-prev', 'n_clicks'),
         Input('btn-next', 'n_clicks'),
         Input({'type': 'friction-item', 'index': ALL}, 'n_clicks'),
         Input('report-store', 'data')],
        [State('pdf-page-store', 'data')]
    )(update_pdf_view_logic)

    # --- 3. AUDIT PANEL ---
    app.callback(
        Output('audit-panel-content', 'children'),
        Input({'type': 'friction-item', 'index': ALL}, 'n_clicks')
    )(update_audit_sidebar_logic)
