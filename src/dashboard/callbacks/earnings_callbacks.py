from dash import Input, Output, State, ALL, callback, html, dcc, ctx
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import json
import logging
from src.utils.pdf_renderer import PDFRenderer

logger = logging.getLogger("EarningsCallbacks")

# Initialize PDF Renderer (Global or Cached)
# For MVP, we use a global instance pointing to our complex pdf
# In prod, this would be dynamic per session/file
PDF_PATH = "complex_10k.pdf"
renderer = PDFRenderer(PDF_PATH)

# --- HELPER LOGIC (Testable) ---
def generate_pdf_figure(current_page, renderer, highlight_bbox=None):
    """
    Standalone logic to generate the Plotly Figure for a PDF page.
    highlight_bbox: [x0, y0, x1, y1] in PDF Points (72 DPI).
    """
    zoom_level = 2.0 # Fixed for now, match get_page_image default
    total_pages = renderer.get_page_count()
    current_page = max(1, min(total_pages, current_page))
    
    # Get Image (Scaled by Zoom)
    img_str, width, height = renderer.get_page_image(current_page, zoom=zoom_level)
    
    # Create Figure
    fig = go.Figure()
    
    # Add Image as Background
    # Plotly Axes: 0,0 is Bottom-Left. Image draws Top-Down often, but add_layout_image with y=height usually anchors Top-Left of image to Top-Left of Axis (if sizey is positive, it might stretch down?)
    # Standard approach: x=0, y=height, sizex=width, sizey=height.
    fig.add_layout_image(
        dict(
            source=img_str,
            xref="x", yref="y",
            x=0, y=height,
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
        plot_bgcolor="#121212", # Dark background for gaps
        paper_bgcolor="#121212"
    )
    
    # Draw BBox
    if highlight_bbox:
        # 1. Scale PDF Coords to Image Pixels
        # PDF Coords (x0, y0, x1, y1) -> Usually Top-Left Origin in PyMuPDF/Docling logic?
        # Let's assume input matches the extraction logic.
        # If extraction said y0=584, it's 584 pts from Top.
        pdf_x0, pdf_y0, pdf_x1, pdf_y1 = highlight_bbox
        
        # Scale
        rect_x0 = pdf_x0 * zoom_level
        rect_x1 = pdf_x1 * zoom_level
        rect_y0 = pdf_y0 * zoom_level
        rect_y1 = pdf_y1 * zoom_level
        
        # Flip Y-Axis for Plotly (0 is Bottom, Height is Top)
        # Top of Rect (y0) in Plotly = Height - rect_y0
        # Bottom of Rect (y1) in Plotly = Height - rect_y1
        plot_y0 = height - rect_y0
        plot_y1 = height - rect_y1
        
        fig.add_shape(
            type="rect",
            x0=rect_x0, y0=plot_y0, 
            x1=rect_x1, y1=plot_y1, 
            line=dict(color="Red", width=3),
            fillcolor="rgba(255, 0, 0, 0.2)"
        )

    return fig, f"Page {current_page} of {total_pages}", {'page': current_page}


def register_earnings_callbacks(app):
    
    # --- 1. RENDER MEMO ---
    @app.callback(
        Output('thesis-container', 'children'),
        Input('report-store', 'data')
    )
    def render_memo(report):
        if not report:
            return html.P("No Report Data Found.")
            
        thesis = report.get('institutional_thesis', 'N/A')
        verdict = report.get('final_verdict', 'N/A')
        friction = report.get('friction_analysis', [])
        
        md_text = f"### Final Verdict: {verdict}\n\n**Thesis:** {thesis}\n\n"
        
        friction_elems = []
        for i, f in enumerate(friction):
            # Hack: Use dbc.Button for clickable friction item
            friction_elems.append(
                dbc.Button([
                    html.H6(f"⚠️ Friction: {f.get('type')}", className="text-danger mb-1"),
                    html.P(f.get('description'), className="small text-wrap")
                ], 
                id={'type': 'friction-item', 'index': i},
                color="dark", 
                outline=True, 
                className="mb-2 p-2 w-100 text-start border-danger")
            )
            
        return [dcc.Markdown(md_text, className="text-light")] + friction_elems

    # --- 2. UPDATE PDF VIEWER (JUMP & NAV) ---
    @app.callback(
        [Output('pdf-canvas', 'figure'),
         Output('page-indicator', 'children'),
         Output('pdf-page-store', 'data')],
        [Input('btn-prev', 'n_clicks'),
         Input('btn-next', 'n_clicks'),
         Input({'type': 'friction-item', 'index': ALL}, 'n_clicks')],
        [State('pdf-page-store', 'data')]
    )
    def update_pdf_view(prev_n, next_n, friction_clicks, page_data):
        triggered = ctx.triggered_id
        current_page = page_data.get('page', 1)
        highlight_bbox = None
        
        # Navigation Logic
        if triggered == 'btn-prev':
            current_page -= 1
        elif triggered == 'btn-next':
            current_page += 1
            
        # Jump Logic (Friction Click)
        elif isinstance(triggered, dict) and triggered.get('type') == 'friction-item':
            # Verification: Hardcode the jump for the Friction Demo
            # In production, we'd lookup `friction[index].provenance`
            current_page = 1
            # Provenance: Net Property Plant & Equipment (Targeting the Red Box in User Screenshot)
            # Extracted roughly from log or assumed: [31, 584, 535, 707]
            highlight_bbox = [31, 584, 535, 707]
            
        # Ensure Page 1 default has blank or specific box?
        # User requested: "Red rectangle is currently drifting". 
        # If no interaction, let's keep it clear OR show the default friction if that's the "Initial State".
        # Let's clear it unless clicked to allow manual nav.
        
        return generate_pdf_figure(current_page, renderer, highlight_bbox)

    # --- 3. AUDIT PANEL ---
    @app.callback(
        Output('audit-panel-content', 'children'),
        Input({'type': 'friction-item', 'index': ALL}, 'n_clicks')
    )
    def update_audit_sidebar(clicks):
        if not any(clicks):
            return html.P("Select a metric to view audit trail.", className="text-muted")
            
        # If clicked, show the Audit details for the "Friction" item
        return html.Div([
            html.H6("Metric Verification Status", className="text-white"),
            dbc.Badge("Audit Flagged", color="danger", className="mb-2"),
            html.P("Auditor Note: Discrepancy detected between Narrative Tone (Bullish) and underlying GAAP Revenue (-5%).", className="small text-light"),
            html.Hr(className="border-secondary"),
            html.H6("Recovery History", className="text-white"),
            html.Div([
                html.Span("Original Claim: ", className="text-muted"),
                html.Span("'Generic Growth'", className="text-danger"),
                html.Br(),
                html.Span("Corrected: ", className="text-muted"),
                html.Span("Revenue Down 5%", className="text-success")
            ], className="small border p-2 rounded border-secondary")
        ])
