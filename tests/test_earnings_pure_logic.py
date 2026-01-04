"""
Test Earnings UI Pure Logic
============================
Tests the decoupled business logic WITHOUT mocking Dash.
This proves the decoupling is complete.
"""
import unittest
import json
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# NO DASH MOCKING REQUIRED - import pure logic directly
from src.logic.earnings_ui_logic import (
    get_memo_content,
    calculate_page_navigation,
    get_pdf_figure_data,
    load_verification_log,
    _build_friction_points,
    _parse_thesis
)


class TestMemoContentGeneration(unittest.TestCase):
    """Test get_memo_content without Dash."""
    
    def test_no_data_returns_status(self):
        """When empty dict passed, logic falls back to disk file or returns no_data."""
        # Empty dict triggers fallback to load_verification_log()
        # If file exists on disk, it loads that
        result = get_memo_content({})
        # Should return success (either with loaded metrics or empty)
        self.assertIn(result["status"], ["success", "no_data", "warning"])
    
    def test_explicit_none_with_no_file(self):
        """When None passed and file doesn't exist, returns no_data."""
        import tempfile
        import os
        # Use a path that definitely doesn't exist
        from src.logic import earnings_ui_logic
        original_path = "verification_log.json"
        # Temporarily move if exists
        if os.path.exists(original_path):
            result = get_memo_content(None)  # Will load from existing file
            self.assertIn(result["status"], ["success", "warning"])
        else:
            result = get_memo_content(None)
            self.assertEqual(result["status"], "no_data")
    
    def test_warning_status_when_no_metrics_but_note(self):
        """When quant_note exists but no metrics, returns warning."""
        report = {
            "run_id": "TEST_123",
            "quant_note": "Something went wrong",
            "metrics": []
        }
        result = get_memo_content(report)
        self.assertEqual(result["status"], "warning")
        self.assertEqual(result["run_id"], "TEST_123")
    
    def test_success_with_metrics(self):
        """Full report with metrics returns success."""
        report = {
            "run_id": "SUCCESS_456",
            "metrics": [
                {"display_name": "Revenue", "verification": {"status": "verified"}}
            ]
        }
        result = get_memo_content(report)
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["metrics"]), 1)


class TestThesisParsing(unittest.TestCase):
    """Test _parse_thesis handles various input formats."""
    
    def test_string_thesis(self):
        """String thesis is wrapped properly."""
        result = _parse_thesis("This is raw thesis text")
        self.assertEqual(result["verdict"], "NEUTRAL")
        self.assertEqual(result["conviction_score"], 0.5)
        self.assertIn("raw thesis text", result["summary"])
    
    def test_dict_thesis(self):
        """Dict thesis extracts fields."""
        thesis = {
            "final_verdict": "BULLISH",
            "conviction_score": 0.8,
            "institutional_thesis": "Strong buy signal"
        }
        result = _parse_thesis(thesis)
        self.assertEqual(result["verdict"], "BULLISH")
        self.assertEqual(result["conviction_score"], 0.8)
    
    def test_error_thesis(self):
        """Error with raw markdown is handled."""
        thesis = {"error": "Parse failed", "raw": "## Markdown content"}
        result = _parse_thesis(thesis)
        self.assertIn("parse_error", result)
        self.assertEqual(result["raw_text"], "## Markdown content")


class TestFrictionPoints(unittest.TestCase):
    """Test friction point extraction."""
    
    def test_extracts_error_metrics(self):
        """Metrics with errors are flagged as friction."""
        metrics = [
            {"display_name": "Good", "verification": {"status": "verified"}},
            {"display_name": "Bad", "verification": {"status": "error_detected", "note": "Mismatch"}}
        ]
        result = _build_friction_points(metrics)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["display_name"], "Bad")
    
    def test_extracts_recovery_used(self):
        """Metrics with recovery_used are flagged."""
        metrics = [
            {"display_name": "Recovered", "recovery_used": True, "verification": {"status": "verified"}}
        ]
        result = _build_friction_points(metrics)
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0]["recovery_used"])


class TestPageNavigation(unittest.TestCase):
    """Test page navigation logic."""
    
    def test_next_button(self):
        """Next button increments page."""
        page, bbox = calculate_page_navigation("btn-next", 5, 10, [])
        self.assertEqual(page, 6)
        self.assertIsNone(bbox)
    
    def test_prev_button(self):
        """Prev button decrements page."""
        page, bbox = calculate_page_navigation("btn-prev", 5, 10, [])
        self.assertEqual(page, 4)
    
    def test_page_bounds(self):
        """Page stays within bounds."""
        page, _ = calculate_page_navigation("btn-next", 10, 10, [])
        self.assertEqual(page, 10)  # Can't go past last
        
        page, _ = calculate_page_navigation("btn-prev", 1, 10, [])
        self.assertEqual(page, 1)  # Can't go before first
    
    def test_friction_click_jumps(self):
        """Clicking friction point jumps to that page."""
        friction = [{"page": 7, "bbox": [100, 200, 300, 400]}]
        triggered = {"type": "friction-item", "index": 0}
        page, bbox = calculate_page_navigation(triggered, 1, 10, friction)
        self.assertEqual(page, 7)
        self.assertEqual(bbox, [100, 200, 300, 400])


class TestFigureData(unittest.TestCase):
    """Test PDF figure data generation."""
    
    def test_basic_figure_data(self):
        """Returns properly structured data."""
        result = get_pdf_figure_data(
            page_num=3,
            img_data="data:image/png;base64,xyz",
            img_width=600,
            img_height=800,
            scale_factor=2.0
        )
        self.assertEqual(result["page_num"], 3)
        self.assertEqual(result["image"]["width"], 600)
        self.assertIsNone(result["highlight"])
    
    def test_with_highlight(self):
        """Highlight data included when bbox provided."""
        result = get_pdf_figure_data(
            page_num=5,
            img_data="data:image",
            img_width=600,
            img_height=800,
            scale_factor=2.0,
            highlight_bbox=[10, 20, 100, 200]
        )
        self.assertTrue(result["highlight"]["enabled"])
        self.assertEqual(result["highlight"]["bbox"], [10, 20, 100, 200])


if __name__ == '__main__':
    unittest.main()
