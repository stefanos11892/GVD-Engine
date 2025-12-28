import os
import sys
import logging
import json

# Setup Path
sys.path.append(os.getcwd())

try:
    from src.agents.auditor import AuditorAgent
except ImportError as e:
    print(f"Import Error: {str(e)}")
    sys.exit(1)

# Configure logging to show Agent output
logging.basicConfig(level=logging.INFO)

def run_controlled_failure():
    print(">>> 1. INITIALIZING AUDITOR (SHORT SELLER)...")
    auditor = AuditorAgent()
    
    # 2. SETUP: Creates a 'Hallucinated' Metric
    fake_metric = {
        "metric_id": "Total Revenue",
        "value_raw": "$50.0B",
        "display_value": "50,000,000,000",
        "provenance": {
            "source_snippet": "Total Revenue ... $10.4B",
            "page": 45,
            "bbox": [100, 100, 50, 10]
        }
    }
    
    # 3. SETUP: The Truth (Context Text)
    # The text clearly says 10.4 Billion, NOT 50.0 Billion
    truth_text = """
    CONSOLIDATED STATEMENTS OF INCOME
    (In billions)
    
    Years Ended December 31,     2024      2023
    Total Revenue                $10.4     $9.8
    Cost of Sales                 (4.2)     (3.9)
    Gross Margin                   6.2       5.9
    """
    
    print(f"\n>>> 2. EXECUTING 'RED TEAM' ATTACK...")
    print(f"    Claim: {fake_metric['value_raw']}")
    print(f"    Truth: $10.4B")
    
    result = auditor.verify_metric(fake_metric, truth_text)
    
    print("\n" + "="*60)
    print("AUDITOR RESPONSE (JSON)")
    print("="*60)
    print(json.dumps(result, indent=2))
    
    # Validation Logic
    status = result.get("verification_status")
    note = result.get("auditor_note")
    
    print("\n" + "="*60)
    print("TEST VERIFICATION")
    print("="*60)
    
    if status == "error_detected":
        print("[PASS] Auditor Caught the Lie.")
    else:
        print(f"[FAIL] Auditor Missed it. Status: {status}")
        
    if note and len(note) > 10:
        print(f"[PASS] Cynical Note Present: \"{note}\"")
    else:
        print("[FAIL] Missing or Weak Note.")

if __name__ == "__main__":
    run_controlled_failure()
