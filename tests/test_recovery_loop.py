import asyncio
import os
import sys
import logging
import json

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
logger = logging.getLogger("StressTest")

from typing import List, Dict, Any

# --- MOCK QUANT AGENT ---
class MockQuant:
    def __init__(self):
        self.call_count = 0

    def extract_metrics(self, markdown_content: str, target_metrics: List[str] = None, feedback: str = None) -> Dict[str, Any]:
        self.call_count += 1
        
        # BBox for the line "Current assets: Cash..." approx from previous run
        # Page 1.
        # We'll use a wide bbox to ensure we catch the text check
        bbox = [31.18, 584.54, 535.75, 707.17] 

        if self.call_count == 1:
            logger.info(">>> [MockQuant] Attempt 1: Injecting HALLUCINATION (Scale Error)...")
            return {
                "metrics": [
                    {
                        "metric_id": "cash_equivalents",
                        "display_name": "Cash and Cash Equivalents",
                        "value_raw": "2,884", # INTENTIONAL ERROR (Missing zero)
                        "provenance": {
                            "source_snippet": "Cash and cash equivalents 28,840",
                            "page": 1,
                            "bbox": bbox
                        }
                    }
                ]
            }
        
        elif feedback:
            logger.info(f">>> [MockQuant] Received Feedback: '{feedback}'")
            logger.info(">>> [MockQuant] Attempt 2: APPLYING CORRECTION...")
            return {
                "metrics": [
                    {
                        "metric_id": "cash_equivalents",
                        "display_name": "Cash and Cash Equivalents",
                        "value_raw": "28,840", # CORRECTED VALUE
                        "provenance": {
                            "source_snippet": "Cash and cash equivalents 28,840",
                            "page": 1,
                            "bbox": bbox
                        }
                    }
                ]
            }
        
        return {"metrics": []}

from typing import List, Dict, Any

async def run_stress_test():
    print(">>> INITIALIZING ADVERSARIAL STRESS TEST...")
    
    # 1. Setup Orchestrator
    orchestrator = EarningsAuditOrchestrator()
    
    # 2. Inject Mock Quant
    orchestrator.quant = MockQuant()
    
    # 3. Validation: Ensure we use the complex PDF
    pdf_path = "complex_10k.pdf"
    if not os.path.exists(pdf_path):
        print("Error: complex_10k.pdf missing.")
        return

    print(">>> EXECUTING WORKFLOW...")
    final_report = await orchestrator.run_workflow(pdf_path)
    
    print("\n" + "="*60)
    print("STRESS TEST RESULTS")
    print("="*60)
    
    # Check Logs
    log_file = "verification_log.json"
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            data = json.load(f)
            
        metrics = data.get("metrics", [])
        if metrics:
            m = metrics[0]
            print(f"Metric: {m.get('metric_id')}")
            print(f"Final Status: Verified? {not m.get('flagged')}")
            print(f"Recovery Used: {m.get('recovery_used')}")
            
            # Show Failure Chain if exists (Wait, successful recovery might simply result in the final state)
            # But we want to see the history. Orchestrator log_history stores it.
            
            print("\nChain of Custody (Orchestrator History):")
            for entry in orchestrator.log_history:
                print(f" - {entry}")
                
            if m.get('recovery_used'):
                print("\n[PASS] RECOVERY LOOP TRIGGERED AND SUCCEEDED.")
            else:
                 print("\n[FAIL] NO RECOVERY DETECTED.")
        else:
            print("[FAIL] No metrics in log.")
    else:
        print("[FAIL] Log file not found.")

if __name__ == "__main__":
    asyncio.run(run_stress_test())
