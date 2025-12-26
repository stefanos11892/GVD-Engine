import sys
import os
import numpy as np
import time

# Fix Path
sys.path.append(os.getcwd())

from src.logic.valuation import ValuationEngine
from src.config import MC_SIMULATIONS, TRADING_DAYS

def test_final_verification():
    print("=== FINAL VERIFICATION SUITE (PHASE 3) ===")
    
    # 1. Config Check
    print(f"[TEST 1] Config Loading...")
    if MC_SIMULATIONS == 10000:
        print(f"   PASS: MC_SIMULATIONS = {MC_SIMULATIONS}")
    else:
        print(f"   FAIL: MC_SIMULATIONS = {MC_SIMULATIONS} (Expected 10000)")
        
    # 2. Vectorization Performance
    print(f"\n[TEST 2] Monte Carlo Performance (Vectorized)...")
    start_time = time.time()
    paths = ValuationEngine.generate_monte_carlo(100.0, 0.35, 0.10, years=5)
    duration = time.time() - start_time
    
    rows, cols = paths.shape
    expected_rows = int(5 * TRADING_DAYS) + 1
    
    if cols == 10000 and rows == expected_rows:
        print(f"   PASS: Generated {cols} paths in {duration:.4f}s.")
    else:
        print(f"   FAIL: Shape mismatch {paths.shape}")

    # 3. Valuation Logic (Regression)
    print(f"\n[TEST 3] Valuation Logic (AMD Proxy)...")
    data = {
        "ticker": "TEST",
        "shares": 1.0,
        "cash": 50,
        "debt": 10,
        "metrics": {"net_income": 5.0} # Yields EPS=5
    }
    # Current Price 100, EPS 5 (PE=20). Growth 15%.
    result = ValuationEngine.calculate_valuation(
        ticker="TEST", current_price=100.0, current_eps=5.0, current_rev=1000.0,
        growth=0.15, margin=0.20, target_pe=25.0, vol=0.35, peg=1.5, method="dcf", data=data
    )
    
    implied_price = result["proj_prices"][5] # Year 5
    print(f"   INFO: Year 5 Implied Price: ${implied_price:.2f}")
    if implied_price > 100:
        print("   PASS: Valuation sanity check OK (Growth > 0 yields higher price)")
    else:
        print("   FAIL: Valuation seems broken (Price didn't grow).")

    # 4. Guardrail Test
    print(f"\n[TEST 4] Safety Guard (@valuation_guard)...")
    try:
        # Trigger error: Division by Zero (simulate bad data)
        # We pass None as data to force a crash inside if we weren't guarded, 
        # but ValuationEngine expects dict. 
        # Let's pass a string as current_price to trigger math error? 
        # Actually generate_monte_carlo is separate.
        # Let's try calling calculate_valuation with garbage that would crash math.
        
        # Passing 'None' for growth should crash math if not guarded
        res = ValuationEngine.calculate_valuation(
            "CRASH", 100, 5, 1000, None, 0.2, 25, 0.35, 1.5, "dcf", {}
        )
        
        if "error" in res:
             print(f"   PASS: Guard caught the error: '{res['error']}'")
             print("   PASS: Returned safe fallback data.")
        else:
             print("   FAIL: Guard did not report error (or calculation succeeded unexpectedly).")
             
    except Exception as e:
        print(f"   FAIL: Guard FAILED. App crashed with: {e}")

if __name__ == "__main__":
    test_final_verification()
