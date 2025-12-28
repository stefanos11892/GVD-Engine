import sys
import os
import pandas as pd
import numpy as np

# Add src to path
sys.path.append(os.path.join(os.getcwd()))

from src.logic.valuation import ValuationEngine

def audit_adbe_case():
    print("--- 1. ADBE Audit (User Input Simulation) ---")
    
    # Inputs guessed from User Screenshot & Report
    # Current Price: $553.00
    # EPS: $10.7
    # Revenue: $23.77B
    # Growth Slider: User set to ~35%? (0.35)
    # Net Margin: 25%? (0.25)
    # Target P/E: 40x (Manual Override)
    # Volatility: 35% (0.35)
    
    ticker = "ADBE"
    current_price = 553.0
    current_eps = 10.7
    current_rev = 23_770_000_000
    
    # Aggressive Inputs
    growth_rate = 0.35 # 35% CAGR is huge for a large cap
    target_margin = 0.25
    target_pe = 40.0
    volatility = 0.35
    peg = 1.5
    method = "pe" # manual override
    
    print(f"INPUTS:\nPrice: ${current_price}\nGrowth: {growth_rate*100}%\nMargin: {target_margin*100}%\nTarget PE: {target_pe}x\n")
    
    # Run Engine
    results = ValuationEngine.calculate_valuation(
        ticker, current_price, current_eps, current_rev, 
        growth_rate, target_margin, target_pe, volatility, peg, method, {}
    )
    
    print("--- DETERMINISTIC PROJECTION ---")
    df = pd.DataFrame(results["table_data"])
    print(df[["year", "revenue", "net_income", "eps", "price", "pe"]])
    
    print("\n--- MONTE CARLO DRIVERS ---")
    print(f"Implied Drift (Annual Return): {results['implied_drift']*100:.2f}%")
    print(f"Implied Rate (r): {results['r_implied']:.4f}")
    
    # Check Step-by-Step Compounding
    # If Growth is 35% for 5 years: 1.35^5 = 4.5x
    # If P/E expands from Current (~50x) to 40x? No, current PE is 553/10.7 = 51x. 
    # If P/E stays high and earnings 4.5x, price 4.5x.
    # Drifts of 40-50% are unsustainable.
    
    # Validation Check
    compound_factor = (1 + growth_rate)**5
    print(f"\nSimple Compounding Check (5 years @ 35%): {compound_factor:.2f}x")
    
    expected_price = current_price * compound_factor * (target_pe / (current_price/current_eps)) 
    print(f"Back-of-napkin Est: {expected_price:.2f}")

    # Run Monte Carlo audit
    mu_adj = results['implied_drift'] + 0.5 * volatility**2
    paths = ValuationEngine.generate_monte_carlo(current_price, volatility, mu=mu_adj, simulations=1000)
    
    final_prices = paths[-1]
    p90 = np.percentile(final_prices, 90)
    print(f"\nMonte Carlo P90: ${p90:.0f}")
    
    if p90 > 10000:
        print("!!! ALERT: P90 > $10,000. Logic seems technically correct given inputs, but inputs are unrealistic.")
    
if __name__ == "__main__":
    audit_adbe_case()
