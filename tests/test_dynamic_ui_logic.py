import unittest
import json
import os
from unittest.mock import MagicMock, patch
import sys

# Add project root to path
sys.path.append(os.getcwd())

# Mock Dash dependencies before loading module
sys.modules['dash'] = MagicMock()
sys.modules['dash_bootstrap_components'] = MagicMock()
sys.modules['plotly.graph_objects'] = MagicMock()

# Now import the module under test
from src.dashboard.callbacks import earnings_callbacks

class TestDynamicUILogic(unittest.TestCase):
    
    def setUp(self):
        # Create a dummy verification_log.json for testing
        self.test_log = {
            "run_id": "TEST_RUN_2025",
            "metrics": [
                {
                    "display_name": "Test Metric Cash",
                    "recovery_used": True,
                    "provenance": {
                        "page": 5,
                        "bbox": [100, 200, 300, 400]
                    },
                    "verification": {
                        "status": "error_detected",
                        "note": "A test note."
                    },
                    "audit_history": [
                        {"attempt": 1, "value_raw": "wrong", "verification": {"note": "bad"}}
                    ]
                }
            ]
        }
        with open("verification_log.json", "w") as f:
            json.dump(self.test_log, f)

        # Mock the renderer globally in the module
        self.mock_renderer = MagicMock()
        self.mock_renderer.get_page_count.return_value = 10
        self.mock_renderer.get_page_image.return_value = ("img_data", 600, 800)
        earnings_callbacks.renderer = self.mock_renderer
        earnings_callbacks.load_verification_log = MagicMock(return_value=self.test_log)


    def tearDown(self):
        # Cleanup
        if os.path.exists("verification_log.json"):
            os.remove("verification_log.json")

    def test_update_pdf_view_jump(self):
        """Test that clicking friction item triggers jump to correct page/bbox"""
        
        # Simulate Context - Friction Item Clicked (Index 0)
        with patch('src.dashboard.callbacks.earnings_callbacks.ctx') as mock_ctx:
            mock_ctx.triggered_id = {'type': 'friction-item', 'index': 0}
            
            # Inputs: prev, next, friction_clicks, page_store
            fig, label, page_store = earnings_callbacks.update_pdf_view_logic(
                0, 0, [1], {'page': 1}
            )
            
            # Verify result
            self.assertEqual(page_store['page'], 5) # Should jump to page 5
            self.assertIn("Page 5", label)

    def test_render_memo(self):
        """Test that buttons are generated"""
        elements = earnings_callbacks.render_memo_logic({})
        
        # Expect 2 elements: Markdown + 1 Button
        self.assertEqual(len(elements), 2)

if __name__ == '__main__':
    unittest.main()
