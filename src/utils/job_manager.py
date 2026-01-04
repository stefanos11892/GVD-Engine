"""
JobManager - Refactored with Proper Concurrency
================================================
Uses ThreadPoolExecutor for background tasks with proper lock protection.
Replaces manual threading.Thread with a managed pool.
"""
import uuid
import asyncio
import logging
import time
import threading
from typing import Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger("JobManager")

# ======================================
# THREAD POOL FOR BACKGROUND JOBS
# ======================================
# Using a shared ThreadPoolExecutor instead of spawning unmanaged threads.
# This provides better resource management and cleanup.
_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="GVD_Worker")


class JobManager:
    """
    Manages background async jobs with thread safety.
    
    All access to self.jobs is protected by _lock to prevent race conditions
    between the main thread (callbacks) and worker threads.
    """
    _instance = None
    _lock = threading.RLock()  # Reentrant lock for nested calls

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
        Uses ThreadPoolExecutor for managed background execution.
        """
        job_id = str(uuid.uuid4())
        
        with self._lock:
            self.jobs[job_id] = {
                "status": "QUEUED",
                "submitted_at": time.time(),
                "pdf_path": pdf_path,
                "result": None,
                "error": None,
                "logs": []
            }
        
        # Submit to executor pool instead of manual threading
        _executor.submit(self._run_worker, job_id, pdf_path)
        
        logger.info(f"Job {job_id} submitted for {pdf_path}")
        return job_id

    def _update_job(self, job_id: str, **kwargs):
        """Thread-safe update of job dictionary fields."""
        with self._lock:
            if job_id in self.jobs:
                self.jobs[job_id].update(kwargs)

    def _run_worker(self, job_id: str, pdf_path: str):
        """
        Worker function executed in thread pool.
        Sets up a new asyncio event loop for the async orchestrator.
        """
        try:
            self._update_job(job_id, status="PROCESSING")
            
            # Lazy import to avoid circular dependencies
            from src.workflows.earnings_audit import EarningsAuditOrchestrator
            
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                orchestrator = EarningsAuditOrchestrator()
                result = loop.run_until_complete(orchestrator.run_workflow(pdf_path))
                
                self._update_job(job_id, result=result, status="COMPLETED")
                logger.info(f"Job {job_id} completed successfully.")
            finally:
                loop.close()
            
        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}", exc_info=True)
            self._update_job(job_id, status="FAILED", error=str(e))

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Returns a copy of the job dict (thread-safe)."""
        with self._lock:
            job = self.jobs.get(job_id)
            return dict(job) if job else None  # Return copy to prevent external mutation

    def get_status(self, job_id: str) -> str:
        """Returns job status (thread-safe)."""
        with self._lock:
            job = self.jobs.get(job_id)
            if not job:
                return "UNKNOWN"
            return job["status"]

    def get_result(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Returns job result if completed (thread-safe)."""
        with self._lock:
            job = self.jobs.get(job_id)
            if job and job["status"] == "COMPLETED":
                return job.get("result")
            return None


# Global Instance
job_manager = JobManager()
