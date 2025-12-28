import sys
import os
import json
import re

# Add src to path
sys.path.append(os.getcwd())

from src.tools.market_data import get_market_data

def test_googl_logic_guard():
    ticker = "GOOGL"
    print(f"--- Debugging logic guard for {ticker} ---")
    
    # 1. Simulate data fetch (same as AnalystAgent)
    market_data = get_market_data(ticker)
    current_price_guard = market_data.get("price")
    
    print(f"Market Data Price: {current_price_guard}")
    print(f"Market Data Raw: {market_data}")
    
    if not current_price_guard:
        print("FAIL: current_price_guard is None. Guard cannot fire.")
        return

    # 2. Simulate Valuation Integration (Calculated Anchor)
    from src.logic.valuation import ValuationEngine
    assumed_growth = 0.12 
    assumed_pe = 20.0     
    assumed_margin = 0.15 
    
    cur_rev = float(market_data.get("revenue_ttm", 0) or 0)
    cur_net = float(market_data.get("net_income_ttm", 0) or 0)
    if cur_rev > 0:
        assumed_margin = cur_net / cur_rev
        
    val_result = ValuationEngine.calculate_valuation(
        ticker=ticker,
        current_price=float(current_price_guard),
        current_eps=float(market_data.get("eps", 0)),
        current_rev=cur_rev,
        growth=assumed_growth,
        margin=assumed_margin,
        target_pe=assumed_pe,
        vol=0.25, peg=1.5, method="pe", data=market_data
    )
    
    if val_result and val_result.get("table_data"):
        math_target_price = val_result["table_data"][0]["price"]
        print(f"Math Anchor (12m Target): ${math_target_price:.2f}")
    
    # 3. Simulate Logic Guard Trigger
    # Suppose Agent returns "BUY" with Target $220
    test_response_json = """
    {
        "ticker": "GOOGL",
        "rating": "BUY",
        "fair_value_range": "$190 - $220",
        "verdict_reasoning": "Great stock."
    }
    """
    
    print("\n--- Testing Logic Guard Trigger ---")
    data = json.loads(test_response_json)
    fv_str = data.get("fair_value_range", "")
    matches = re.findall(r"[\d,\.]+", fv_str)
    
    def safe_float(s):
        try: return float(s.replace(",", ""))
        except: return 0.0

    values = [safe_float(m) for m in matches if safe_float(m) > 0]
    if values:
        target_high = max(values)
        print(f"Parsed Target High: {target_high}")
        print(f"Current Price: {current_price_guard}")
        
        if float(current_price_guard) > target_high:
            print("GUARD TRIGGERED: Price > Target.")
            if "BUY" in data.get("rating"):
                print("ACTION: Converting BUY to HOLD.")
        else:
            print("GUARD SILENT: Price <= Target.")

if __name__ == "__main__":
    test_googl_logic_guard()
