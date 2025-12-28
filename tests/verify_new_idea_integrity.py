import sys
import os
import json
import re

# Mock Data
mock_originator_output = """Based on the live screen, I have identified **AMZN** as the top candidate.
Amazon is a great compounder. AWS is the engine."""

mock_analyst_data = {
    "ticker": "AMZN",
    "pe": "32.88", # String as usually returned
    "pe_ratio": 32.88,
    "market_cap": "2.49T",
    "scores": {"quality": 95}
}

def test_callback_logic():
    print("--- Testing UI Logic Integrity ---")
    
    ticker = "AMZN"
    
    # 1. Parsing Originator (Should NOT find table)
    raw_narrative = mock_originator_output
    clean_narrative = re.sub(r'\|.*\|', '', raw_narrative).strip()
    
    deal_data = {
        "ticker": ticker,
        "market_cap": "Checking...",
        "pe": "N/A",
        "thesis": clean_narrative
    }
    
    print(f"Initial Deal Data: {deal_data}")
    
    # 2. Enrich with Analyst Data (The Happy Path)
    analyst_data = mock_analyst_data
    if analyst_data:
        if "market_cap" in analyst_data: deal_data["market_cap"] = analyst_data.get("market_cap")
        if "pe_ratio" in analyst_data: deal_data["pe"] = str(analyst_data.get("pe_ratio"))

    print(f"After Analyst Enrich: {deal_data}")
    
    # Check Result
    if deal_data["pe"] == "32.88":
        print("PASS: P/E correctly sourced from Analyst.")
    else:
        print("FAIL: P/E not updated.")

    # 3. Validation Layer (Mock)
    # If Analyst failed
    deal_data_bad = {"ticker": "AMZN", "market_cap": "Checking...", "pe": "N/A"}
    
    print("\n--- Testing Fallback to Live Data ---")
    
    # Simulate the validation fetch logic locally
    # (Since we can't import the full dash app context easily, we invoke the tool directly)
    from src.tools.market_data import get_market_data
    
    if deal_data_bad["pe"] in ["N/A", "Checking..."]:
        print("Triggering Live Validation...")
        real_data = get_market_data("AMZN")
        if real_data.get("pe"):
             deal_data_bad["pe"] = f"{real_data['pe']:.2f}"
             
    print(f"After Live Fetch: {deal_data_bad}")
    
    if deal_data_bad["pe"] != "N/A":
        print("PASS: Validation Layer successfully fetched real P/E.")
    else:
        print("FAIL: Validation Layer did not update P/E.")

if __name__ == "__main__":
    test_callback_logic()
