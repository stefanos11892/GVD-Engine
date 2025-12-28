import asyncio
import os
import sys
import logging

# Setup Path
sys.path.append(os.getcwd())

# MONKEY PATCH for HuggingFace (Symlink Fix)
import shutil
import huggingface_hub.file_download
def _force_copy(src, dst, new_blob=False):
    try:
        shutil.copy2(src, dst)
    except Exception as e:
        print(f"Copy failed: {e}")
huggingface_hub.file_download._create_symlink = _force_copy

from src.workflows.earnings_audit import EarningsAuditOrchestrator

# Configure Logging
logging.basicConfig(level=logging.INFO)

async def run_demo():
    print(">>> INITIALIZING ORCHESTRATOR...")
    orchestrator = EarningsAuditOrchestrator()
    
    # Use the complex 10K we created earlier
    pdf_path = "complex_10k.pdf"
    if not os.path.exists(pdf_path):
        print("Error: complex_10k.pdf not found. Run tests/demo_earnings_capabilities.py first.")
        return

    print(f">>> RUNNING AUDIT WORKFLOW ON {pdf_path}...")
    result = await orchestrator.run_workflow(pdf_path)
    
    print("\n>>> WORKFLOW COMPLETE")
    print(f"    Metrics Processed: {len(result.get('metrics', []))}")
    print(f"    Run ID: {result.get('run_id')}")
    
    log_path = "verification_log.json"
    if os.path.exists(log_path):
        print(f"\n>>> AUDIT LOG GENERATED: {os.path.abspath(log_path)}")
    else:
        print("\n>>> ERROR: Log file not found.")

if __name__ == "__main__":
    asyncio.run(run_demo())
