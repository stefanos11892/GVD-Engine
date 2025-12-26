import sys
import os
import json
from src.agents.analyst import AnalystAgent

# Fix Path
sys.path.append(os.getcwd())

def test_independence():
    print("=== TESTING ANALYST INDEPENDENCE ===")
    agent = AnalystAgent()
    
    # Fake Dashboard Data (unrealistic values)
    fake_data = {
        "ticker": "ADBE",
        "current_price": 500.0,
        "base_case": {
            "revenue_growth": 0.50, # CLAIM: 50% Growth (Reality is ~10-12%)
            "target_pe": 100        # CLAIM: 100x P/E
        }
    }
    
    context = json.dumps(fake_data, indent=2)
    prompt = f"Analyze ADBE. STRICTLY use this dashboard data for valuation metrics: {context}"
    
    print("Sending Fake Scenario: ADBE growing 50%, P/E 100x.")
    response = agent.run(prompt)
    
    print("\n--- AGENT RESPONSE ---")
    if "50%" in response or "100" in response:
        print("Agent referenced the fake numbers.")
    else:
        print("Agent ignored the fake numbers.")
        
    print(response)

if __name__ == "__main__":
    test_independence()
