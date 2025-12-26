from dash import html
import dash_bootstrap_components as dbc

def create_metric_card(title, value, icon, color="primary", id_value=None):
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.I(className=f"bi {icon} display-4 text-{color} mb-2"),
            ], className="text-center"),
            html.H5(title, className="text-center text-muted"),
            html.H3(value, className="text-center font-weight-bold", id=id_value),
        ])
    ], className="h-100 shadow-sm")
