from dash import html
import dash_bootstrap_components as dbc

def render_thesis_card(ticker, status, narrative, deal_memo):
    """
    Renders the v0-designed Investment Thesis Card.
    
    Args:
        ticker (str): Ticker symbol.
        status (str): "PASS", "FAIL", or "HOLD".
        narrative (str): Top-level narrative text.
        deal_memo (dict): Dictionary containing 'ticker', 'market_cap', 'pe', 'thesis'.
    """
    
    # Status Dot Logic
    status_colors = {
        "PASS": "dot-green",
        "FAIL": "dot-red",
        "HOLD": "bg-warning" # Fallback
    }
    dot_class = status_colors.get(status, "bg-secondary")
    
    return html.Div([
        # Header
        html.Div([
            html.Div([
                html.Span("Investment Thesis", className="fw-bold"),
                html.Div([
                    html.Span(className=f"dot {dot_class}"),
                    status
                ], className="badge-status-dot")
            ], className="flex-between w-100")
        ], className="card-principal-header"),
        
        # Body
        html.Div([
            # Narrative Section (Condensed)
            html.Div([
                html.P(narrative, className="text-body-technical mb-0")
            ], className="mb-4 pb-4 border-bottom border-light border-opacity-10"),
            
            # Deal Memo Section
            html.Div([
                html.H3("Deal Memo", className="text-label text-uppercase mb-3", style={"fontSize": "0.75rem"}),
                
                # Metrics Grid (The v0 Magic)
                html.Div([
                    html.Div([
                        html.Div("Ticker", className="text-label-micro"),
                        html.Div(deal_memo.get("ticker", ticker), className="metric-value-lg")
                    ]),
                    html.Div([
                        html.Div("Market Cap", className="text-label-micro"),
                        html.Div(deal_memo.get("market_cap", "N/A"), className="metric-value-lg")
                    ]),
                    html.Div([
                        html.Div("P/E Ratio", className="text-label-micro"),
                        html.Div(deal_memo.get("pe", "N/A"), className="metric-value-lg")
                    ]),
                ], className="grid-metrics"),
                
                # Thesis Statement (Clean Box) - Only if content exists
                html.Div([
                    html.Div("Thesis", className="text-label-micro mb-2"),
                    html.Div(deal_memo.get("thesis", ""), className="thesis-container text-body-technical")
                ]) if deal_memo.get("thesis") else None
            ])
        ], className="card-principal-body")
        
    ], className="card-principal shadow-lg")
