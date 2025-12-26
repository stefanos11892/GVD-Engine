import numpy as np

def run_deep_audit():
    # INPUTS FROM SCREENSHOT
    current_price = 215.04
    current_eps = 2.02
    current_rev = 32.038 * 1e9 # 32B
    growth = 0.50 # 50% CAGR
    margin = 0.25 # 25% Net Margin (Target)
    
    # Net Debt Logic (Fixed V5)
    # Assume AMD data: Cash=5B, Debt=2.5B, Shares=1.6B
    # V5 Logic: If shares missing, derive. But let's assume shares ~1.6B (MarketCap 350B / 215)
    shares = 350.098 * 1e9 / 215.04
    cash = 5.0 * 1e9  # Approx
    debt = 2.5 * 1e9  # Approx
    net_cash_per_share = (cash - debt) / shares
    if net_cash_per_share > current_price * 0.8: net_cash_per_share = 0
    print(f"Net Cash Per Share: ${net_cash_per_share:.2f}")

    # 1. Earnings Stream (3-Stage)
    stream_eps = []
    term_growth = 0.03
    sim_eps = current_eps
    
    print("\n--- Earnings Stream ---")
    # Years 1-5 (50% Growth)
    for i in range(5):
        sim_eps *= (1 + growth)
        stream_eps.append(sim_eps)
        print(f"Year {i+1}: ${sim_eps:.2f} (Growth: {growth*100:.0f}%)")
        
    # Years 6-10 (Fade to 3%)
    current_g = growth
    step = (growth - term_growth) / 5.0
    for i in range(5):
        current_g -= step
        if current_g < term_growth: current_g = term_growth
        sim_eps *= (1 + current_g)
        stream_eps.append(sim_eps)
        print(f"Year {6+i}: ${sim_eps:.2f} (Fade Growth: {current_g*100:.1f}%)")

    # 2. Solver (Implied WACC)
    low = 0.02
    high = 0.50
    r_final = 0.10
    
    def calculate_fair_value(r_try):
        eff_term_g = min(term_growth, r_try - 0.015)
        pv_sum = 0
        for i, eps_val in enumerate(stream_eps):
            t = i + 1
            pv_sum += eps_val / ((1 + r_try)**t)
        
        final_eps = stream_eps[-1]
        tv = (final_eps * (1 + eff_term_g)) / (r_try - eff_term_g)
        pv_tv = tv / ((1 + r_try)**10)
        return pv_sum + pv_tv + net_cash_per_share

    for _ in range(30):
        mid = (low + high) / 2
        fv = calculate_fair_value(mid)
        if fv > current_price:
            low = mid # Need higher rate to lower value
        else:
            high = mid
    r_final = (low + high) / 2
    
    print(f"\n--- Solver Results ---")
    print(f"Current Price: ${current_price:.2f}")
    print(f"Implied WACC (r): {r_final*100:.2f}%")
    print(f"Effective Terminal Growth: {min(term_growth, r_final-0.015)*100:.2f}%")
    
    # Check Price at Year 5 (2029)
    # Using Rolling PV Logic
    r_use = r_final
    eff_term_g = min(term_growth, r_use - 0.015)
    
    # We are at Year 5. Remaining stream is Year 6-10 (indices 5-9)
    remaining_stream = stream_eps[5:]
    pv_remaining = 0
    for i, eps_val in enumerate(remaining_stream):
        t = i + 1
        pv_remaining += eps_val / ((1 + r_use)**t)
        
    final_eps = stream_eps[-1]
    tv = (final_eps * (1 + eff_term_g)) / (r_use - eff_term_g)
    # TV is at Year 10. We are at Year 5. Dist = 5.
    pv_tv = tv / ((1 + r_use)**5)
    
    price_2029 = pv_remaining + pv_tv + net_cash_per_share
    
    print(f"\n--- 2029 Projection ---")
    print(f"Year 5 EPS: ${stream_eps[4]:.2f}")
    print(f"Implied Price 2029: ${price_2029:.2f}")
    print(f"Implied P/E 2029: {price_2029 / stream_eps[4]:.1f}x")
    
    # Analysis
    print(f"\n--- WHY IS IT ${price_2029:.0f}? ---")
    print(f"1. You assumed 50% growth.")
    print(f"2. But the Current Price is only ${current_price:.0f}.")
    print(f"3. To reconcile this, the model implies the Market requires a {r_final*100:.1f}% Return (WACC).")
    print(f"4. This massive discount rate ({r_final*100:.1f}%) crushes the future value.")
    print(f"   - PV of TV is heavily discounted.")
    print(f"   - P/E contracts from {current_price/current_eps:.0f}x today to {price_2029/stream_eps[4]:.0f}x.")

if __name__ == "__main__":
    run_deep_audit()
