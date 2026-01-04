import asyncio
import logging
import os
import sys
import time

# Add project root
sys.path.append(os.getcwd())

from src.utils.job_manager import JobManager
from src.workflows.earnings_audit import EarningsAuditOrchestrator

# Setup logging - Stream to specific file to avoid clutter
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("debug_perf.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("DebugPerf")

async def run_perf_test():
    pdf_path = "temp/uploads/4b154bb9_4e3fa-2025-02-12-07-10-34_d7dcb.pdf"
    
    if not os.path.exists(pdf_path):
        logger.error(f"File not found: {pdf_path}")
        return

    logger.info(f"--- STARTING PERF TEST ON {pdf_path} ---")
    start_time = time.time()
    
    orchestrator = EarningsAuditOrchestrator()
    
    try:
        logger.info("1. Initializing Orchestrator...")
        # We run it directly to await it (JobManager runs in thread)
        result = await orchestrator.run_workflow(pdf_path)
        
        duration = time.time() - start_time
        logger.info(f"--- SUCCESS ---")
        logger.info(f"Total Duration: {duration:.2f} seconds")
        logger.info(f"Result Keys: {result.keys()}")
        
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"--- FAILED after {duration:.2f}s ---")
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_perf_test())
