"""
JSON Utilities for LLM Response Parsing
=======================================
Pure Python functions with no Dash dependencies.
Moved from agent_callbacks.py to enable standalone testing.
"""
import re
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("JSONUtils")


def safe_json_parse(raw_str: str) -> Dict[str, Any]:
    """
    Safely extract and parse JSON from LLM response strings.
    
    Handles:
    - Markdown code fences (```json ... ```)
    - Embedded JSON in larger text
    - Malformed or missing JSON
    
    Returns empty dict on failure (never raises).
    """
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


def extract_json_array(raw_str: str) -> list:
    """
    Extract a JSON array from an LLM response string.
    
    Returns empty list on failure.
    """
    if not raw_str:
        return []
    try:
        clean = raw_str.replace("```json", "").replace("```", "").strip()
        match = re.search(r'\[[\s\S]*\]', clean)
        if match:
            return json.loads(match.group(0))
        return []
    except Exception as e:
        logger.warning(f"JSON array parse failed: {e}")
        return []


def robust_json_extract(raw_str: str, key: str, default: Any = None) -> Any:
    """
    Extract a specific key from a JSON response.
    
    Args:
        raw_str: Raw LLM output
        key: Key to extract
        default: Default value if key not found
        
    Returns:
        Value for key or default
    """
    data = safe_json_parse(raw_str)
    return data.get(key, default)
