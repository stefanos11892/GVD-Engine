import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/workflows/earnings', name='Earnings Season')

layout = dbc.Container([
    html.H2("Earnings Season Analysis", className="mb-4"),
    html.P("Analyze earnings reports and 10-Ks.", className="text-muted"),
    
    html.Div([
        html.Div("Upload Documents", className="card-principal-header"),
        html.Div([
            dcc.Upload(
                id='upload-data',
                children=html.Div(['Drag and Drop or ', html.A('Select Files')]),
                style={
                    'width': '100%', 'height': '60px', 'lineHeight': '60px',
                    'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px',
                    'textAlign': 'center', 'margin': '10px'
                },
                multiple=True
            ),
            dbc.Button("Analyze", id="btn-analyze-earnings", color="info", className="mt-2"),
        ], className="card-principal-body")
    ], className="card-principal mb-4"),
    
    html.Div([
        html.Div("Analysis Results", className="card-principal-header"),
        html.Div([
            dcc.Loading(
                id="loading-earnings",
                type="default",
                children=html.Div(id="earnings-output", children="Results will appear here...")
            )
        ], className="card-principal-body")
    ], className="card-principal")
])
