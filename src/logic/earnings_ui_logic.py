"""
Earnings UI Pure Logic Module
==============================
Contains business logic for the Earnings workflow, decoupled from Dash.
Returns plain Python data structures (dicts, lists) instead of Dash components.

This allows:
- Unit testing without mocking Dash
- Reuse in CLI tools or APIs
- Clean separation of concerns
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger("EarningsUILogic")


# ======================================
# DATA LOADING
# ======================================
def load_verification_log(log_path: str = "verification_log.json") -> Optional[Dict[str, Any]]:
    """Load verification log from disk."""
    if not os.path.exists(log_path):
        return None
    try:
        with open(log_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load log: {e}")
        return None


# ======================================
# MEMO CONTENT GENERATION
# ======================================
def get_memo_content(report: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate memo content data from a report.
    
    Returns a dictionary with structured data that can be rendered
    by any UI framework (Dash, CLI, API response, etc.)
    
    Structure:
    {
        "status": "no_data" | "warning" | "success",
        "run_id": str,
        "message": str (optional),
        "thesis": {...} (optional),
        "metrics": [...] (optional),
        "friction_points": [...] (optional)
    }
    """
    log_data = report if report else load_verification_log()
    
    if not log_data:
        return {
            "status": "no_data",
            "message": "No Analysis Data Found. Please Run Workflow."
        }
    
    run_id = log_data.get('run_id', 'Unknown')
    metrics = log_data.get('metrics', [])
    quant_note = log_data.get('quant_note') or log_data.get('quant_error')
    
    # Warning case - no metrics but has note
    if not metrics and quant_note:
        return {
            "status": "warning",
            "run_id": run_id,
            "message": quant_note
        }
    
    # Success case - build full response
    result = {
        "status": "success",
        "run_id": run_id,
        "metrics": metrics
    }
    
    # Extract thesis data
    thesis = log_data.get('institutional_thesis')
    if thesis:
        result["thesis"] = _parse_thesis(thesis)
    
    # Build friction points for sidebar
    result["friction_points"] = _build_friction_points(metrics)
    
    return result


def _parse_thesis(thesis: Any) -> Dict[str, Any]:
    """Parse thesis data, handling both dict and string formats."""
    if isinstance(thesis, str):
        return {
            "verdict": "NEUTRAL",
            "conviction_score": 0.5,
            "summary": thesis[:200] + "..." if len(thesis) > 200 else thesis,
            "raw_text": thesis
        }
    elif isinstance(thesis, dict):
        # Handle error case with raw markdown
        if 'error' in thesis and 'raw' in thesis:
            return {
                "verdict": "NEUTRAL",
                "conviction_score": 0.5,
                "raw_text": thesis.get('raw', ''),
                "parse_error": thesis.get('error')
            }
        
        # Normal dict case
        return {
            "verdict": thesis.get('final_verdict', 'NEUTRAL'),
            "conviction_score": thesis.get('conviction_score', 0),
            "summary": thesis.get('institutional_thesis', ''),
            "economic_reality": thesis.get('economic_reality'),
            "capital_allocation": thesis.get('capital_allocation'),
            "moat_margin": thesis.get('moat_margin'),
            "narrative_integrity": thesis.get('narrative_integrity'),
            "key_risks": thesis.get('key_risks', [])
        }
    return {}


def _build_friction_points(metrics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Extract friction points (metrics needing attention) from metrics list."""
    friction_points = []
    
    for i, metric in enumerate(metrics):
        verification = metric.get('verification', {})
        status = verification.get('status', 'unknown')
        
        # Flag metrics that had issues
        if status in ['error_detected', 'unverified'] or metric.get('recovery_used'):
            friction_points.append({
                "index": i,
                "display_name": metric.get('display_name', f'Metric {i}'),
                "status": status,
                "note": verification.get('note', ''),
                "recovery_used": metric.get('recovery_used', False),
                "page": metric.get('provenance', {}).get('page', 1),
                "bbox": metric.get('provenance', {}).get('bbox')
            })
    
    return friction_points


# ======================================
# PDF NAVIGATION LOGIC
# ======================================
def calculate_page_navigation(
    triggered_id: Any,
    current_page: int,
    total_pages: int,
    friction_points: List[Dict[str, Any]]
) -> Tuple[int, Optional[List[float]]]:
    """
    Calculate next page and highlight based on navigation action.
    
    Args:
        triggered_id: The ID of the element that triggered the action
        current_page: Current page number (1-indexed)
        total_pages: Total number of pages in document
        friction_points: List of friction point dicts with page/bbox info
    
    Returns:
        (new_page, highlight_bbox) - new page number and optional bbox to highlight
    """
    highlight_bbox = None
    new_page = current_page
    
    # Handle friction point clicks
    if isinstance(triggered_id, dict) and triggered_id.get('type') == 'friction-item':
        idx = triggered_id.get('index', 0)
        if idx < len(friction_points):
            fp = friction_points[idx]
            new_page = fp.get('page', current_page)
            highlight_bbox = fp.get('bbox')
    
    # Handle next/prev navigation
    elif triggered_id == 'btn-next':
        new_page = min(current_page + 1, total_pages)
    elif triggered_id == 'btn-prev':
        new_page = max(current_page - 1, 1)
    elif triggered_id == 'report-store':
        new_page = 1  # Reset on new report
    
    return new_page, highlight_bbox


# ======================================
# FIGURE DATA GENERATION
# ======================================
def get_pdf_figure_data(
    page_num: int,
    img_data: str,
    img_width: float,
    img_height: float,
    scale_factor: float,
    highlight_bbox: Optional[List[float]] = None
) -> Dict[str, Any]:
    """
    Generate figure data for PDF page display.
    
    Returns a dict that can be used to construct a Plotly figure.
    This separates the data computation from the Plotly/Dash specifics.
    """
    return {
        "page_num": page_num,
        "image": {
            "source": img_data,
            "width": img_width,
            "height": img_height,
            "scale_factor": scale_factor
        },
        "highlight": {
            "enabled": highlight_bbox is not None,
            "bbox": highlight_bbox
        } if highlight_bbox else None
    }
