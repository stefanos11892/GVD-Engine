import threading
import uuid
import asyncio
import logging
import time
from typing import Dict, Any, Optional
from src.workflows.earnings_audit import EarningsAuditOrchestrator

logger = logging.getLogger("JobManager")

class JobManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(JobManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.jobs: Dict[str, Dict[str, Any]] = {}
        self._initialized = True

    def submit_job(self, pdf_path: str) -> str:
        """
        Submits a PDF for analysis. Returns a unique job_id.
        Runs the async orchestrator in a separate thread.
        """
        job_id = str(uuid.uuid4())
        self.jobs[job_id] = {
            "status": "QUEUED",
            "submitted_at": time.time(),
            "pdf_path": pdf_path,
            "result": None,
            "error": None,
            "logs": []
        }
        
        # Spawn Thread
        thread = threading.Thread(target=self._run_worker, args=(job_id, pdf_path))
        thread.daemon = True
        thread.start()
        
        logger.info(f"Job {job_id} submitted for {pdf_path}")
        return job_id

    def _run_worker(self, job_id: str, pdf_path: str):
        """
        Worker thread function. Sets up a new asyncio event loop for the orchestrator.
        """
        try:
            self.jobs[job_id]["status"] = "PROCESSING"
            
            # Create new loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            orchestrator = EarningsAuditOrchestrator()
            
            # Run Workflow
            result = loop.run_until_complete(orchestrator.run_workflow(pdf_path))
            
            self.jobs[job_id]["result"] = result
            self.jobs[job_id]["status"] = "COMPLETED"
            logger.info(f"Job {job_id} completed successfully.")
            
            loop.close()
            
        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}", exc_info=True)
            self.jobs[job_id]["status"] = "FAILED"
            self.jobs[job_id]["error"] = str(e)

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            return self.jobs.get(job_id)

    def get_status(self, job_id: str) -> str:
        with self._lock:
            job = self.jobs.get(job_id)
            if not job:
                return "UNKNOWN"
            return job["status"]

# Global Instance
job_manager = JobManager()
