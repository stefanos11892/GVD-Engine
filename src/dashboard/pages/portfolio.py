import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
import pandas as pd
import plotly.express as px
import os
from src.dashboard.components.cards import create_metric_card

dash.register_page(__name__, name='Portfolio')

# Load data via DataManager
from src.utils.data_manager import data_manager

# Refresh data on page load (in a real app, use a callback or store)
# Refresh data on page load (in a real app, use a callback or store)
data_manager.load_data()
df = data_manager.get_portfolio_df()

# Create charts
if not df.empty:
    # Ensure Market Value is numeric
    df['Market Value'] = pd.to_numeric(df['Market Value'], errors='coerce').fillna(0)
    fig_allocation = px.pie(df, values='Market Value', names='Ticker', title='Portfolio Allocation', hole=0.3)
    fig_allocation.update_layout(template="plotly_dark")
else:
    fig_allocation = {}

layout = dbc.Container([
    html.H2("Portfolio Overview", className="mb-4"),
    
    # Metrics Row
    dbc.Row([
        dbc.Col(create_metric_card("Total Value", f"${data_manager.get_total_value():,.2f}", "bi-wallet2", "success", id_value="val-total-value"), width=4),
        dbc.Col(create_metric_card("Cash Balance", f"${data_manager.get_cash_balance():,.2f}", "bi-cash-coin", "info", id_value="val-cash-balance"), width=4),
        dbc.Col(create_metric_card("Invested", f"${data_manager.get_holdings_value():,.2f}", "bi-graph-up-arrow", "warning", id_value="val-invested"), width=4),
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            html.Div([
                html.Div("Holdings", className="card-principal-header"),
                html.Div([
                    dag.AgGrid(
                        id="portfolio-grid",
                        rowData=df.to_dict("records"),
                        columnDefs=[{"field": i} for i in df.columns],
                        defaultColDef={"filter": True, "sortable": True, "resizable": True},
                        className="ag-theme-alpine-dark",
                        style={"height": "400px"}
                    )
                ], className="card-principal-body p-0")
            ], className="card-principal")
        ], width=12, className="mb-4")
    ]),
    
    dbc.Row([
        dbc.Col([
            html.Div([
                html.Div("Allocation", className="card-principal-header"),
                html.Div([
                    dcc.Graph(figure=fig_allocation)
                ], className="card-principal-body p-0")
            ], className="card-principal h-100")
        ], width=6),
        dbc.Col([
            html.Div([
                html.Div("Update Portfolio", className="card-principal-header"),
                html.Div([
                    dcc.Upload(
                        id='upload-portfolio',
                        children=html.Div([
                            'Drag and Drop or ',
                            html.A('Select PDF Statement')
                        ]),
                        style={
                            'width': '100%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '10px'
                        },
                        multiple=False
                    ),
                    html.Div(id="upload-status")
                ], className="card-principal-body")
            ], className="card-principal h-100")
        ], width=6)
    ])
])
