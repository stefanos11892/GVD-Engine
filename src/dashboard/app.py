import dash
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc
import sys
import os

# Add GVD_Engine to sys.path to allow imports from src
# We assume app.py is in GVD_Engine/src/dashboard/
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(project_root)

from src.dashboard.components.sidebar import create_sidebar
# Import callbacks to register them
import src.dashboard.callbacks.agent_callbacks
import src.dashboard.callbacks.data_callbacks
from src.dashboard.callbacks.earnings_callbacks import register_earnings_callbacks

# Initialize the app with a dark theme and Bootstrap Icons
app = Dash(
    __name__, 
    use_pages=True, 
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP],
    suppress_callback_exceptions=True
)

# Register Earnings Logic
register_earnings_callbacks(app)

# Define the layout
app.layout = dbc.Container([
    dbc.Row([
        # Sidebar
        create_sidebar(),
        
        # Main Content Area
        dbc.Col([
            dash.page_container
        ], width=10, className="offset-2 p-4")
    ])
], fluid=True)

if __name__ == "__main__":
    app.run(debug=True, port=8052)
