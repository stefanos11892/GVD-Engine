from dash import Input, Output, State, callback, html
import dash_bootstrap_components as dbc
import base64
import os
from src.utils.data_manager import data_manager

@callback(
    Output("upload-status", "children"),
    Output("portfolio-grid", "rowData"),
    Output("portfolio-grid", "columnDefs"),
    Output("val-total-value", "children"),
    Output("val-cash-balance", "children"),
    Output("val-invested", "children"),
    Input("upload-portfolio", "contents"),
    State("upload-portfolio", "filename"),
    prevent_initial_call=True
)
def update_portfolio(contents, filename):
    if contents is None:
        return "", [], [], "", "", ""
    
    try:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        
        # Ensure uploads directory exists
        upload_dir = os.path.join(os.getcwd(), "GVD_Engine", "data", "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, filename)
        
        with open(file_path, "wb") as f:
            f.write(decoded)
            
        # Trigger DataManager ingestion
        result_msg = data_manager.ingest_statement(file_path)
        
        # Fetch updated data
        df = data_manager.get_portfolio_df()
        total_val = f"${data_manager.get_total_value():,.2f}"
        cash_bal = f"${data_manager.get_cash_balance():,.2f}"
        invested = f"${data_manager.get_holdings_value():,.2f}"
        
        # Prepare Grid Data
        row_data = df.to_dict("records")
        col_defs = [{"field": i} for i in df.columns]
        
        alert = dbc.Alert(f"Success: {result_msg}", color="success", dismissable=True)
        
        return alert, row_data, col_defs, total_val, cash_bal, invested
        
    except Exception as e:
        error_alert = dbc.Alert(f"Error processing file: {str(e)}", color="danger", dismissable=True)
        return error_alert, [], [], "Error", "Error", "Error"
