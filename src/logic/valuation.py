import numpy as np
from datetime import datetime
from src.logic.guards import valuation_guard
from src.config import (
    TERMINAL_GROWTH_RATE, DEFAULT_DISCOUNT_RATE, GORDON_GUARD_BUFFER,
    MC_SIMULATIONS, TRADING_DAYS, MC_DRIFT_CAP_MULTIPLIER, 
    DEFAULT_SHARES
)

class ValuationEngine:
    """
    Core Logic Query Refactor (Phase 1, 2, 3).
    Encapsulates V5 Convergence Model (DCF) and P/E Glide Path Logic.
    Enhanced with Vectorized Monte Carlo, Safety Guards, and Central Config.
    """
    
    @staticmethod
    @valuation_guard
    def calculate_valuation(ticker, current_price, current_eps, current_rev, growth, margin, 
                          target_pe, vol, peg, method, data):
        """
        Main entry point for valuation.
        Returns a dictionary with key metrics.
        """
        
        # --- 0. Setup & Data Parsing ---
        # Robust Shares Logic (V5 Persistence Fix)
        cash = data.get("cash", 0)
        debt = data.get("debt", 0)
        raw_shares = data.get("shares")
        
        metrics = data.get("metrics", {})
        net_income = metrics.get("net_income")
        
        derived_shares = None
        if current_eps and current_eps > 0 and net_income:
            derived_shares = net_income / current_eps
            
        if raw_shares and raw_shares > 1_000_000:
             shares = raw_shares
        elif derived_shares:
             shares = derived_shares
        else:
             shares = DEFAULT_SHARES 

        # Net Cash Logic with Cap
        if shares > 1000:
            net_cash_per_share = (cash - debt) / shares
        else:
            net_cash_per_share = 0
            
        # Sanity Guard: Net Cash shouldn't exceed 80% of price
        if net_cash_per_share > current_price * 0.8:
            net_cash_per_share = 0
            
        # --- 1. Earnings Stream Generation (3-Stage) ---
        stream_eps = []
        term_growth = TERMINAL_GROWTH_RATE
        
        sim_eps = current_eps if (current_eps and current_eps > 0) else (current_price/25.0)
        
        # Stage 1: Years 1-5 (User Growth)
        for i in range(5):
            sim_eps *= (1 + growth)
            stream_eps.append(sim_eps)
            
        # Stage 2: Years 6-10 (Linear Fade)
        if growth > term_growth:
            fade_step = (growth - term_growth) / 5.0
            current_g = growth
            for i in range(5):
                current_g -= fade_step
                if current_g < term_growth: current_g = term_growth
                sim_eps *= (1 + current_g)
                stream_eps.append(sim_eps)
        else:
            for i in range(5):
                sim_eps *= (1 + term_growth)
                stream_eps.append(sim_eps)

        # --- 2. Solver (Implied WACC) - V5 Convergence ---
        def solve_dcf_price(r_try):
            # Gordon Guardrail: g <= r - 1.5%
            eff_term_g = min(term_growth, r_try - GORDON_GUARD_BUFFER)
            
            # Safety: Ensure denominator is never zero or negative
            if r_try <= eff_term_g:
                eff_term_g = r_try - 0.01  # Force minimum 1% spread
            
            pv_sum = 0
            for i, eps_val in enumerate(stream_eps):
                t = i + 1
                pv_sum += eps_val / ((1 + r_try)**t)
            
            final_eps = stream_eps[-1]
            tv = (final_eps * (1 + eff_term_g)) / (r_try - eff_term_g)
            pv_tv = tv / ((1 + r_try)**10)
            
            return pv_sum + pv_tv + net_cash_per_share

        # Binary Search for r
        low = 0.02
        high = 0.50
        r_implied = DEFAULT_DISCOUNT_RATE
        
        if method == "dcf":
            target_to_match = current_price
            val_low = solve_dcf_price(low)
            val_high = solve_dcf_price(high)
            
            if target_to_match > val_low: 
                r_implied = low
            elif target_to_match < val_high:
                r_implied = high
            else:
                for _ in range(25):
                    mid = (low + high) / 2
                    val = solve_dcf_price(mid)
                    if val > target_to_match:
                        low = mid 
                    else:
                        high = mid
                r_implied = (low + high) / 2
        
        # --- 3. Projection Loop (Years 1-5) ---
        current_year = datetime.now().year
        proj_years = [current_year]
        proj_prices = [current_price]
        table_data = [] # Structured data for UI to render
        
        base_rev = current_rev
        
        # P/E Glide Logic Prep
        if current_eps and current_eps > 0:
            current_pe_ratio = current_price / current_eps
        else:
            current_pe_ratio = target_pe
            
        for year in range(1, 6):
            # Fundamentals
            future_rev = base_rev * ((1 + growth)**year)
            future_net = future_rev * margin
            year_idx = year - 1
            future_eps = stream_eps[year_idx] # Aligned
            
            future_implied_price = 0
            used_pe = 0
            
            if method == "dcf":
                # Rolling DCF Logic
                r_use = r_implied
                eff_term_g = min(term_growth, r_use - GORDON_GUARD_BUFFER)
                
                pv_remaining = 0
                remaining_stream = stream_eps[year:] 
                for i, eps_val in enumerate(remaining_stream):
                     t = i + 1 
                     pv_remaining += eps_val / ((1 + r_use)**t)
                     
                final_eps = stream_eps[-1]
                tv = (final_eps * (1 + eff_term_g)) / (r_use - eff_term_g)
                pv_tv = tv / ((1 + r_use)**(10 - year))
                
                future_implied_price = pv_remaining + pv_tv + net_cash_per_share
                used_pe = future_implied_price / future_eps if future_eps else 0
                
            else:
                # P/E Logic
                horizon = 10.0
                progress = year / horizon 
                weight_target = progress
                weight_current = 1.0 - weight_target
                
                eff_start_pe = current_pe_ratio if current_pe_ratio > 0 else target_pe
                used_pe = (eff_start_pe * weight_current) + (target_pe * weight_target)
                future_implied_price = future_eps * used_pe

            proj_years.append(current_year + year)
            proj_prices.append(future_implied_price)
            
            table_data.append({
                "year": current_year + year,
                "revenue": future_rev,
                "growth_pct": growth,
                "net_income": future_net,
                "eps": future_eps,
                "price": future_implied_price,
                "pe": used_pe
            })
            
        # --- 4. Monte Carlo Prep ---
        final_price = proj_prices[-1]
        start_price = proj_prices[0]
        if start_price > 0 and final_price > 0:
            total_return = final_price / start_price
            if total_return > MC_DRIFT_CAP_MULTIPLIER: total_return = MC_DRIFT_CAP_MULTIPLIER
            implied_drift = (total_return ** (1/5)) - 1
        else:
            implied_drift = growth

        return {
            "proj_years": proj_years,
            "proj_prices": proj_prices,
            "table_data": table_data,
            "implied_drift": implied_drift,
            "r_implied": r_implied,
            "net_cash_per_share": net_cash_per_share
        }

    @staticmethod
    def generate_monte_carlo(current_price, volatility, mu, years=5, simulations=MC_SIMULATIONS):
        """
        Vectorized Geometric Brownian Motion (Phase 2 Refactor).
        Uses NumPy cumulative sum for optimization.
        """
        dt = 1/TRADING_DAYS
        days = int(years * TRADING_DAYS)
        
        # 1. Pre-calculate Drift per Step (Scalar)
        drift_per_step = (mu - 0.5 * volatility**2) * dt
        
        # 2. Generate Random Shocks (Tensor: days x simulations)
        # Vectorized generation (Heavy but NumPy handles it in ms)
        shocks = np.random.normal(0, volatility * np.sqrt(dt), size=(days, simulations))
        
        # 3. Add Drift and Shock
        # shape: (days, sims)
        log_returns = drift_per_step + shocks
        
        # 4. Cumulative Sum over Time (Axis 0 = days)
        # This gives the Total Log Return at each step t relative to t=0
        cumulative_log_returns = np.cumsum(log_returns, axis=0)
        
        # 5. Convert to Price Paths
        # S_t = S_0 * exp(Sum(r_t))
        # Prepend 0 to cumulative sum so Day 0 is S_0 * exp(0) = S_0
        
        # Optimization: We usually want to view the paths including Start Price.
        # Create full paths array
        paths = np.zeros((days + 1, simulations))
        paths[0] = current_price
        
        paths[1:] = current_price * np.exp(cumulative_log_returns)
            
        return paths
