import sys
import os
import pandas as pd
import numpy as np
from dash import html

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock Dash Page Registry to allow import without App
import dash
dash.register_page = lambda *args, **kwargs: None

from src.tools.market_data import get_market_data
from src.dashboard.pages.workflows.forecasting import update_simulation

def run_audit():
    tickers = ["NVDA", "TSLA", "JNJ", "KO", "XOM", "AMD", "INTC", "JPM", "AMZN", "NET"]
    results = []

    print(f"{'Ticker':<6} | {'PE':<6} | {'Growth':<6} | {'Base Price':<10} | {'MC Median':<10} | {'Var %':<6} | {'Status':<6}")
    print("-" * 80)

    for ticker in tickers:
        try:
            # 1. Fetch Data
            real_data = get_market_data(ticker)
            price = real_data.get("price") or 100.0
            
            # 2. Smart Defaults Logic (Replicated from fetch_agent_data)
            eps_raw = real_data.get("eps")
            try:
                eps = float(eps_raw) if eps_raw else None
            except:
                eps = None

            current_pe = price / eps if (eps and eps > 0) else 25.0
            if current_pe > 150: current_pe_capped = 150 # Cap for input only, logic uses "eff_start_pe"
            else: current_pe_capped = current_pe

            rev = real_data.get("revenue_ttm")
            net = real_data.get("net_income_ttm")
            
            # Logic Update: If Margin is negative, default to 15% (Target)
            if rev and net and rev > 0:
                calc_margin = net / rev
                smart_margin = 0.15 if calc_margin < 0 else calc_margin
            else:
                smart_margin = 0.20
            
            smart_growth = 0.15 # Default
            smart_vol = real_data.get("volatility") or 0.35
            
            # Construct Data Dict for Update
            data_dict = {
                "current_price": price,
                "eps": eps,
                "metrics": {"revenue": rev, "net_income": net},
                "cash": real_data.get("cash", 0),
                "debt": real_data.get("debt", 0),
                "shares": real_data.get("shares"),
                "base_case": {
                    "revenue_growth": smart_growth,
                    "target_net_margin": smart_margin,
                    "target_pe": 25
                }
            }

            # 3. Run Simulation (Base Case: PEG=1.5, Method='pe')
            # update_simulation(growth, margin, pe_override, vol, peg, method, data)
            fig_proj, fig_mc, table, stats_ui = update_simulation(
                smart_growth, smart_margin, 25, smart_vol, 1.5, "pe", data_dict
            )

            # 4. Extract Results (PE Mode)
            tbody = table.children[1]
            last_row = tbody.children[-1]
            price_str = last_row.children[-1].children.split("(")[0].replace("$", "").strip().replace(",", "")
            implied_price_2029 = float(price_str)

            median_div = stats_ui.children[1].children[1]
            median_str = median_div.children.replace("$", "").replace(",", "").strip()
            mc_median = float(median_str)
            
            variance = abs(mc_median - implied_price_2029) / implied_price_2029
            variance_pct = variance * 100
            status = "PASS" if variance_pct < 10 else "FAIL"
            
            # 6. Flash Crash Check
            first_row = tbody.children[0]
            price_str_1 = first_row.children[-1].children.split("(")[0].replace("$", "").strip().replace(",", "")
            price_year_1 = float(price_str_1)
            if current_pe > 50 and price_year_1 < (price * 0.8): status = "CRASH"

            # --- DCF GAP CHECK (V4) ---
            # Run in DCF mode and check if Year 1 starts near Current Price
            # Ideally we check Year 0 but table starts at Year 1.
            # V4 Logic: Price(t) = PV(Remaining) + NetCash.
            # Year 1 Price should be consistent with Current Price. 
            # If r_implied is solved correctly, Price_0 = Current. 
            # Price_1 ~= Current * (1+r) (roughly).
            # Let's check variance of Year 1 vs Current Price.
            
            fig_proj_dcf, _, table_dcf, _ = update_simulation(
                smart_growth, smart_margin, 25, smart_vol, 1.5, "dcf", data_dict
            )
            tbody_dcf = table_dcf.children[1]
            row_1_dcf = tbody_dcf.children[0]
            p1_dcf_str = row_1_dcf.children[-1].children.split("(")[0].replace("$", "").strip().replace(",", "")
            p1_dcf = float(p1_dcf_str)
            
            # Gap Check: Is Year 1 within 50% of Current? (Just sane?)
            # Or better: check graph data for Year 0 point?
            # fig_proj_dcf['data'][0]['y'][0] should be Year 0 Price (Current).
            
            try:
                # Trace 0 is the line. x[0]=Year0, y[0]=Price0.
                year0_price = fig_proj_dcf.data[0].y[0]
                gap_var = abs(year0_price - price) / price
                dcf_status = "PASS" if gap_var < 0.05 else f"FAIL ({gap_var*100:.1f}%)"
            except:
                dcf_status = "ERR"

            print(f"{ticker:<6} | {current_pe:<6.1f} | {implied_price_2029:<9.2f} | {mc_median:<9.2f} | {variance_pct:<5.1f} | {status:<5} | DCF_Gap: {dcf_status}")
            
            
            results.append({
                "Ticker": ticker,
                "PE": current_pe,
                "Implied_2029": implied_price_2029,
                "MC_Median": mc_median,
                "Variance": variance_pct,
                "Status": status
            })

        except Exception as e:
            print(f"{ticker:<6} | ERROR: {str(e)}")

if __name__ == "__main__":
    print("Running Lead Quantitative Audit...\n")
    run_audit()
