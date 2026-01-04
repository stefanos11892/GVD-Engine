import sys
import os
from unittest.mock import MagicMock

# Mock deps to avoid ImportErrors
sys.modules['dash'] = MagicMock()
sys.modules['dash_bootstrap_components'] = MagicMock()
sys.modules['plotly.graph_objects'] = MagicMock()

sys.path.append(os.getcwd())

import src.dashboard.callbacks.earnings_callbacks as ec

print("File:", ec.__file__)
print("Attributes:", dir(ec))

if hasattr(ec, 'render_memo_logic'):
    print("SUCCESS: render_memo_logic found.")
else:
    print("FAILURE: render_memo_logic NOT found.")
