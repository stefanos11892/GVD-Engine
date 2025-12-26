def calculate_projections(current_price, current_pe, target_pe, growth, years=5):
    print(f"--- Valuation Verification (Current PE: {current_pe}, Target PE: {target_pe}) ---")
    
    # Calculate EPS from Price and PE
    eps = current_price / current_pe
    print(f"Derived EPS: ${eps:.2f}")
    
    print("\nYear | Projected EPS | Target PE Used | Implied Price | % Change")
    print("-" * 65)
    
    prices = []
    
    for year in range(1, years + 1):
        future_eps = eps * ((1 + growth) ** year)
        
        # CURRENT LOGIC: Jump straight to Target PE
        pe_used = target_pe
        
        future_price = future_eps * pe_used
        pct_change = ((future_price - current_price) / current_price) * 100
        
        prices.append(future_price)
        print(f"{2024+year} | ${future_eps:.2f}          | {pe_used}             | ${future_price:.2f}       | {pct_change:+.1f}%")

    return prices

# Simulation: PLTR Scenario 
# Price: ~$90 (approx from user screenshot/memory)
# EPS: ~$0.43 (from screenshot) -> PE is roughly 209
# User sets Target PE to 40 (optimistic but much lower than 200)

current_price = 194.17 # From screenshot
eps = 0.43 # From screenshot
current_pe = current_price / eps
target_pe = 40.0 
growth = 0.38 # From screenshot slider

print(f"SCENARIO: PLTR Trading at ${current_price} with EPS ${eps} (P/E {current_pe:.1f})")
calculate_projections(current_price, current_pe, target_pe, growth)
