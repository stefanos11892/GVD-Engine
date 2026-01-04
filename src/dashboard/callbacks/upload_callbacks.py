import base64
import os
import shutil
import uuid
from dash import Input, Output, State, callback, html, ctx
from src.utils.job_manager import job_manager

UPLOAD_DIR = "temp/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def register_upload_callbacks(app):
    
    @app.callback(
        [Output("current-job-store", "data"),
         Output("upload-status-msg", "children")],
        Input("upload-current-10k", "contents"),
        State("upload-current-10k", "filename")
    )
    def handle_upload(contents, filename):
        if not contents:
            return None, ""

        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)

        # Save to temp
        safe_filename = f"{uuid.uuid4().hex[:8]}_{filename}"
        file_path = os.path.join(UPLOAD_DIR, safe_filename)
        
        with open(file_path, "wb") as f:
            f.write(decoded)

        # Submit Job
        job_id = job_manager.submit_job(file_path)
        
        return {"job_id": job_id}, f"Job Started: {job_id} for {filename}"
