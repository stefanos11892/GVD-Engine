import sys
import os
import json
from src.agents.analyst import AnalystAgent

# Fix Path
sys.path.append(os.getcwd())

def test_analyst_methodology():
    print("=== VERIFYING ANALYST METHODOLOGY UPGRADE ===")
    agent = AnalystAgent()
    
    # Run Agent (Short context for speed, but mentioning methodology)
    # We expect the agent to follow the NEW system prompt.
    print("Running Agent on 'NVDA'...")
    response = agent.run("Analyze NVDA")
    
    print("\nRAW RESPONSE:")
    print(response)
    
    # Validation
    try:
        # Extract JSON if wrapped in markdown
        json_str = response
        if "```json" in response:
             json_str = response.split("```json")[1].split("```")[0]
        elif "{" in response:
             start = response.find("{")
             end = response.rfind("}")
             json_str = response[start:end+1]
             
        data = json.loads(json_str)
        
        required_fields = ["fair_value_range", "methodology_check", "scores", "verdict_reasoning"]
        missing = [f for f in required_fields if f not in data]
        
        if not missing:
            print("\n[PASS] JSON Structure Valid & Upgraded.")
            print(f"Fair Value: {data['fair_value_range']}")
            print(f"Methodology: {data['methodology_check']}")
        else:
            print(f"\n[FAIL] Missing upgraded fields: {missing}")
            
    except Exception as e:
        print(f"\n[FAIL] JSON Parsing Error: {e}")

if __name__ == "__main__":
    test_analyst_methodology()
