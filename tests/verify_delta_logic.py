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

from src.logic.delta_engine import DeltaEngine

# Configure Logging
logging.basicConfig(level=logging.INFO)

async def run_verification():
    print(">>> 1. INITIALIZING DELTA ENGINE...")
    engine = DeltaEngine()
    
    current_pdf = "current_year.pdf"
    prior_pdf = "prior_year.pdf"
    
    if not os.path.exists(current_pdf) or not os.path.exists(prior_pdf):
        print("Error: Test PDFs missing. Run setup_delta_test.py first.")
        return

    print(">>> 2. COMPARING DOCUMENTS...")
    result = await engine.compare_documents(current_pdf, prior_pdf)
    
    print("\n" + "="*60)
    print("DELTA ANALYSIS RESULTS")
    print("="*60)
    print(json.dumps(result, indent=2))
    
    # Save Report
    with open("delta_report.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"\n[INFO] Report saved to: {os.path.abspath('delta_report.json')}")
    
    # Assertions
    print("\n" + "="*60)
    print("VERIFICATION CHECKS")
    print("="*60)
    
    # 1. Vagueness Check
    retreats = result.get("numerical_retreats", [])
    if any("$50" in r['retreat_from'] and 'significant' in r['retreat_to'] for r in retreats):
        print("[PASS] Vagueness Detected: '$50 million' -> 'significant amount'")
    else:
        print(f"[FAIL] Numerical Retreat Missed. Found: {retreats}")

    # 2. Entropy Check
    entropy = result.get("entropy_analysis", {})
    if entropy.get("is_obfuscated"):
        print(f"[PASS] Obfuscation Detected: Density dropped by {entropy.get('change_pct')}%")
    else:
        print(f"[FAIL] Obfuscation Missed. Change: {entropy.get('change_pct')}%")

    # 3. Omission Check
    omissions = result.get("silent_omissions", [])
    # Clean header text might vary depending on parser (e.g. "2. Cryptocurrency Volatility" vs "Cryptocurrency Volatility")
    # We check if "Cryptocurrency" appears in any omission string
    if any("Cryptocurrency" in o for o in omissions):
        print("[PASS] Silent Omission Detected: 'Cryptocurrency Volatility' removed.")
    else:
        print(f"[FAIL] Omission Missed. Found: {omissions}")

if __name__ == "__main__":
    asyncio.run(run_verification())
