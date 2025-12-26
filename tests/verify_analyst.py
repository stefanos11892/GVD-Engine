
import asyncio
import json
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from src.agents.analyst import AnalystAgent

async def test_analyst():
    print("--- Testing Analyst Agent (JSON Validity) ---")
    agent = AnalystAgent()
    
    ticker = "AAPL"
    print(f"Running Analyst on: {ticker}")
    
    # We use the async run method
    output = await agent.run_async(f"Analyze {ticker}")
    
    print("\n[RAW OUTPUT START]")
    print(output)
    print("[RAW OUTPUT END]\n")
    
    # Validation Logic
    try:
        # Clean markdown wrappers if present
        clean_output = output.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_output)
        
        required_keys = ["ticker", "rating", "scores", "key_metrics", "verdict_reasoning"]
        missing_keys = [k for k in required_keys if k not in data]
        
        if missing_keys:
            print(f"❌ FAILED: Missing JSON keys: {missing_keys}")
            sys.exit(1)
            
        if "quality" not in data.get("scores", {}):
            print("❌ FAILED: Missing 'quality' score.")
            sys.exit(1)
            
        print("✅ SUCCESS: Output is valid JSON and contains all required schemas.")
        print(f"Verdict: {data['rating']}")
        print(f"Quality Score: {data['scores']['quality']}")
        
    except json.JSONDecodeError as e:
        print(f"❌ FAILED: Invalid JSON. Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_analyst())
