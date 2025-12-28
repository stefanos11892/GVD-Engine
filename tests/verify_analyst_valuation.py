import sys
import os
import json

# Add src to path
sys.path.append(os.getcwd())

from src.agents.analyst import AnalystAgent

def test_analyst_math_anchor():
    print("--- Testing Analyst Valuation Anchor ---")
    
    agent = AnalystAgent()
    ticker = "GOOG" # Test with GOOG as user requested
    
    print(f"Running Analyst for {ticker}...")
    # We simulate the prompt input
    response = agent.run(f"Input: {ticker}. Analyze this stock.")
    
    print("\n--- RAW RESPONSE ---")
    print(response)
    
    # Parse JSON
    try:
        cleaned = response
        if "```json" in response:
            cleaned = response.split("```json")[1].split("```")[0].strip()
        data = json.loads(cleaned)
        
        target_range = data.get("fair_value_range", "N/A")
        rating = data.get("rating", "N/A")
        
        print(f"\nParsed Target Range: {target_range}")
        print(f"Parsed Rating: {rating}")
        
        if "12-month Target Price" in response or "INTERNAL VALUATION MODEL" in response: 
             # Note: We can't see the internal context easily unless we print it in the agent.
             # But we can infer success if the numbers look closer to current price (~170) than old hallucination (130).
             pass

    except Exception as e:
        print(f"JSON Parse Error: {e}")

if __name__ == "__main__":
    test_analyst_math_anchor()
