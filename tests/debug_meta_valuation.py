import sys
import os
import json
import re

sys.path.append(os.getcwd())

from src.tools.market_data import get_market_data
from src.logic.valuation import ValuationEngine

def debug_meta():
    ticker = "META"
    print(f"--- DIAGNOSING META VALUATION ---")
    
    # 1. Fetch Data
    market_data = get_market_data(ticker)
    price = market_data.get("price")
    print(f"Data Source Price: {price}")
    print(f"Data Source EPS: {market_data.get('eps')}")
    print(f"Data Source Rev: {market_data.get('revenue_ttm')}")
    
    if not price:
        print("ERROR: No Price found.")
        return

    # 2. Run Valuation (Current Assumptions)
    # The Analyst Agent uses these Hardcoded defaults:
    assumed_growth = 0.12 
    assumed_pe = 20.0
    
    # Recalculate margin
    cur_rev = float(market_data.get("revenue_ttm", 0) or 0)
    cur_net = float(market_data.get("net_income_ttm", 0) or 0)
    assumed_margin = cur_net / cur_rev if cur_rev > 0 else 0.15
    print(f"Calculated Margin: {assumed_margin:.2%}")
    
    val_result = ValuationEngine.calculate_valuation(
        ticker=ticker,
        current_price=float(price),
        current_eps=float(market_data.get("eps", 0)),
        current_rev=cur_rev,
        growth=assumed_growth,
        margin=assumed_margin,
        target_pe=assumed_pe,
        vol=0.25, peg=1.5, method="pe", data=market_data
    )
    
    math_target = 0
    if val_result and val_result.get("table_data"):
        math_target = val_result["table_data"][0]["price"]
        print(f"Calculated Math Anchor (12m): ${math_target:.2f}")
        
    # 3. Analyze Discrepancy
    diff = math_target - float(price)
    print(f"Diff: ${diff:.2f}")
    if math_target < float(price):
        print("CONCLUSION: The Math Anchor is LOWER than Current Price.")
        print("Reason: Assumptions (12% Growth / 20x PE) are too conservative for this stock.")
    else:
        print("CONCLUSION: Anchor is HIGHER. The Guard should NOT have triggered.")

if __name__ == "__main__":
    debug_meta()
