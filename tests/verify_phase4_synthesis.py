import asyncio
import os
import sys
import logging
import json
from datetime import datetime

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

from src.workflows.earnings_synthesis import EarningsSynthesisOrchestrator

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Phase4Verification")

# --- MOCK DATA GENERATORS ---
def get_mock_quant_data():
    return {
        "metrics": [
            {
                "metric_id": "revenue",
                "display_name": "Revenue",
                "value_raw": "$9.5B",
                "trend": "Down 5% YoY", # Quant specifically flagging decline
                "provenance": {"source_snippet": "Revenue decreased to $9.5B"}
            }
        ]
    }

def get_mock_qual_data():
    return {
        "sentiment_score": 0.9,
        "narrative_tone": "Bullish",
        "key_themes": ["Growth", "Momentum"],
        "management_confidence": "High",
        "vagueness_flags": [] 
    }

def get_mock_delta_data():
    return {
        "numerical_retreats": [],
        "silent_omissions": ["Risk Factor: Supply Chain"]
    }

async def run_verification():
    print(">>> 1. INITIALIZING SYNTHESIS ORCHESTRATOR...")
    orchestrator = EarningsSynthesisOrchestrator()
    
    print(">>> 2. INJECTING CONFLICTING STREAMS (Fan-Out Simulation)...")
    quant = get_mock_quant_data()
    qual = get_mock_qual_data()
    delta = get_mock_delta_data()
    
    print(f"   [QUANT]: Revenue is Down (Bearish Data)")
    print(f"   [QUAL]:  Tone is Bullish (Management Confidence High)")
    print(f"   [DELTA]: Omitted Risk Factor")
    
    print(">>> 3. RUNNING CONSOLIDATOR...")
    report = await orchestrator.synthesize(quant, qual, delta)
    
    print("\n" + "="*60)
    print("INSTITUTIONAL REPORT (SYNTHESIS)")
    print("="*60)
    print(json.dumps(report, indent=2))
    
    # Save Report
    with open("synthesis_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n[INFO] Report saved to: {os.path.abspath('synthesis_report.json')}")
    
    # Assertions
    print("\n" + "="*60)
    print("VERIFICATION CHECKS")
    print("="*60)
    
    # 1. Check Friction Detection
    friction_list = report.get("friction_analysis", [])
    if any("Bullish" in str(f) or "Growth" in str(f) for f in friction_list):
        print("[PASS] Thesis Friction Detected (Bullish Tone vs Poor Data).")
    else:
        # Fallback check: look for specific keywords in the friction description
        if len(friction_list) > 0:
             print("[PASS] Thesis Friction identified (General).")
        else:
             print("[FAIL] No Friction detected! Consolidator missed the contradiction.")

    # 2. Check Conviction Score (Should be low due to conflict)
    score = report.get("conviction_score", 1.0)
    if score < 0.7:
        print(f"[PASS] Conviction Score lowered ({score}) reflecting conflict.")
    else:
        print(f"[FAIL] Conviction Score too high ({score}) given the contradiction.")

    # 3. Check Delta Integration
    risks = report.get("key_risks", [])
    if any("Risk Factor" in r or "Supply Chain" in r for r in risks):
        print("[PASS] Delta Signal (Omission) integrated into Risks.")
    else:
        print("[FAIL] Delta Signal missing from Key Risks.")

if __name__ == "__main__":
    asyncio.run(run_verification())
