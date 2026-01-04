from dash import Input, Output, State, callback, no_update
from src.utils.job_manager import job_manager
import json
import os

def register_status_callbacks(app):
    
    @app.callback(
        [Output("upload-status-msg", "children", allow_duplicate=True),
         Output("job-poll-interval", "disabled"),
         Output("report-store", "data", allow_duplicate=True)],
        Input("job-poll-interval", "n_intervals"),
        State("current-job-store", "data"),
        prevent_initial_call=True
    )
    def poll_job_status(n, job_data):
        if not job_data:
            return "No active job", True, no_update
            
        job_id = job_data.get("job_id")
        status = job_manager.get_status(job_id)
        
        if status == "COMPLETED":
            # Load result
            job = job_manager.get_job(job_id)
            result = job.get("result", {})
            return f"Analysis Complete: Run {result.get('run_id')}", True, result
            
        elif status == "FAILED":
             job = job_manager.get_job(job_id)
             return f"Analysis Failed: {job.get('error')}", True, no_update
             
        else:
            # Still Processing
            return f"Processing... ({status})", False, no_update

    # Enable Polling when Job Starts
    @app.callback(
        Output("job-poll-interval", "disabled", allow_duplicate=True),
        Input("current-job-store", "data"),
        prevent_initial_call=True
    )
    def start_polling(job_data):
        if job_data and job_data.get("job_id"):
            return False # Enable interval
        return True
