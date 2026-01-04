from src.agents.base_agent import BaseAgent
from src.tools.market_data import get_market_data
from src.tools.web_search import search_web


class AnalystAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Analyst",
            role="Lead Researcher",
            temperature=0.1, # Low temp for consistent reasoning
            system_instruction="""
[PERSONA]
You are the **Lead Equity Researcher** at a top-tier Long/Short Hedge Fund.
Your mandate is to produce **Institutional-Grade Investment Memos** that scrutinize quality, valuation, and risk.
You strictly adhere to **Value Investing Principles** (Graham/Dodd, Buffett, Klarman).

[DATA SOURCE PRIORITY - "TRUST BUT VERIFY"]
You will receive [DASHBOARD SCENARIO] (User's Inputs) and [WEB SEARCH] (Market Reality).
1.  **Analyze the Scenario**: "If the company achieves these growth/margin targets, is it undervalued?"
2.  **Reality Check**: "Are these inputs realistic compared to [WEB SEARCH] consensus?"
    *   If User Growth (e.g. 50%) >> Histotical/Consensus Growth (e.g. 10%), YOU MUST FLAG THIS as "Aggressive/Unrealistic".
    *   Do NOT blindy accept the dashboard numbers as truth. Treat them as a "Bull Case assumption" to be audited.

3.  **Current Price vs Fair Value Check**:
    *   Compare Current Price to your calculated Fair Value Range.
    *   **CRITICAL RULE**: If Current Price > High End of Fair Value, rating CANNOT be "BUY". It must be "HOLD" or "SELL".
    *   Do not promote a stock as "Undervalued" if your own math says it is "Overvalued".

[METHODOLOGY & MODELS]
You must apply the following rigorous frameworks to your analysis:
1.  **Dupont Analysis**: Deconstruct ROE. Is it driven by Margins (Pricing Power), Turnover (Efficiency), or Leverage (Risk)?
2.  **Quality of Earnings**: Calculate **Cash Conversion Ratio** (Operating Cash Flow / Net Income). If < 80%, flag as "Low Quality" (aggressive accounting).
3.  **Capital Allocation**: Compare **ROIC vs WACC**. Is the company destroying value by growing?
4.  **Forensic Check**: Scrutinize **Stock-Based Compensation (SBC)**. If SBC > 20% of OCF, treat it as a cash expense and downgrade FCF.
5.  **Reverse DCF**: instead of guessing price, ask "What growth is priced in?".

[TASK]
Perform a deep-dive Due Diligence on the [Ticker].

[OUTPUT FORMAT]
Response must be in **STRICT JSON**.
{
    "ticker": "SYMBOL",
    "rating": "STRONG BUY" | "BUY" | "HOLD" | "SELL" | "SHORT",
    "fair_value_range": "$XXX - $XXX",
    "scores": {
        "quality": 0-100,      // Weighted avg of ROIC, Moat, Margins
        "valuation": 0-100,    // 100 = Deep Value, 0 = Overvalued
        "management": 0-100    // Capital Allocation focus
    },
    "score_rationale": {
        "quality": "One sentence explaining the quality score (e.g. 'High due to wide moat and stable margins').",
        "valuation": "One sentence explaining valuation (e.g. 'Low because P/E is 50x vs historical 20x').",
        "management": "One sentence on capital allocation (e.g. 'Excellent buyback track record')."
    },
    "methodology_check": {
        "roic_vs_wacc": "Spread positive/negative",
        "earnings_quality": "High/Low (Cash Conv > 1x)",
        "sbc_impact": "Dilutive/Manageable"
    },
    "detailed_analysis": "A comprehensive paragraph (100-150 words) synthesizing the Dupont, Forensic, and Valuation findings. Explain the 'Story' of the stock.",
    "bull_case": "Specific catalyst (e.g. margin expansion, new cycle).",
    "bear_case": "Specific risk (e.g. commoditization, regulation).",
    "verdict_reasoning": "Synthesize the Dupont, ROIC, and Valuation analysis into a decisive conclusion."
}
"""
        )

    def log_debug(self, message):
        try:
            with open("debug_analyst.log", "a") as f:
                import datetime
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{timestamp}] {message}\n")
        except:
            pass

    def run(self, user_input, context=None):
        # Attempt to extract ticker from input OR context
        text_to_scan = f"{user_input} {context if context else ''}"
        words = text_to_scan.replace("\n", " ").replace(":", " ").replace("*", " ").split()
        ticker = None
        for word in words:
            # Simple heuristic: Upper case, 2-5 chars, alpha only. 
            # In a real app, we'd validate against a master list.
            clean_word = word.strip(".,()[]")
            if clean_word.isupper() and 2 <= len(clean_word) <= 5 and clean_word.isalpha():
                # Avoid common false positives
                if clean_word not in ["BUY", "SELL", "HOLD", "THE", "AND", "FOR", "NOT", "USD", "EUR", "ROIC", "WACC", "FCF", "DCF", "SBC"]:
                    ticker = clean_word
                    break
        
        # Logic Guard Data Prep
        current_price_guard = None
        if ticker:
            print(f"DEBUG: Fetching data for {ticker}...")
            market_data = get_market_data(ticker)
            current_price_guard = market_data.get("price")
            
            print(f"DEBUG: Searching web for {ticker} financials...")
            search_results = search_web(f"{ticker} investor relations annual report roic sbc")
            
            context = f"{context}\n\nMARKET DATA:\n{market_data}\n\nWEB SEARCH:\n{search_results}"
            
            # --- INTERNAL VALUATION ENGINE INTEGRATION ---
            try:
                from src.logic.valuation import ValuationEngine
                
                # 1. Dynamic Assumptions (Smarter Building Blocks)
                # Growth: Use PEG if available, bounded [5%, 25%]
                # PE: Use Current PE if reasonable, bounded [10x, 35x]
                
                cur_pe = float(market_data.get("pe", 0) or 0)
                cur_price = float(market_data.get("price", 0) or 0)
                
                # Robust EPS parsing - handle string values like "2.50" or "-1.20"
                raw_eps = market_data.get("eps", 0)
                try:
                    cur_eps = float(str(raw_eps).replace(",", "")) if raw_eps else 0.0
                except (ValueError, TypeError):
                    cur_eps = 0.0
                
                # Heuristic: If High Quality (High ROIC implied), use higher multiple
                assumed_pe = 20.0 
                if cur_pe > 0:
                     # Blend Current PE and Base Case (Conservative Glide)
                     if cur_pe > 35: assumed_pe = 30.0 # Cap Euphoria
                     elif cur_pe < 10: assumed_pe = 12.0 # Cap Pessimism
                     else: assumed_pe = (cur_pe + 20.0) / 2 # Midpoint
                
                # Heuristic: Growth from PEG
                # PEG = PE / (Growth * 100) -> Growth = (PE / PEG) / 100
                # We use a standard PEG of 1.5 (Reasonable for Quality Growth)
                peg_target = 1.5
                if cur_pe > 5:
                    implied_growth = (cur_pe / peg_target) / 100.0
                    # Bound validity: Min 6% (GDP+), Max 25% (Sustainability Cap)
                    assumed_growth = max(0.06, min(0.25, implied_growth))
                else:
                    assumed_growth = 0.12 # Fallback for unprofitable/distressed
                
                # Log the dynamic inputs for debug
                self.log_debug(f"Dynamic Inputs: PE={cur_pe} -> Growth={assumed_growth:.1%} (PEG {peg_target})")

                cur_rev = float(market_data.get("revenue_ttm", 0) or 0)
                cur_net = float(market_data.get("net_income_ttm", 0) or 0)
                assumed_margin = 0.15
                if cur_rev > 0:
                    assumed_margin = cur_net / cur_rev
                
                # 2. Run Math
                val_result = ValuationEngine.calculate_valuation(
                    ticker=ticker,
                    current_price=cur_price,
                    current_eps=cur_eps,
                    current_rev=cur_rev,
                    growth=assumed_growth,
                    margin=assumed_margin,
                    target_pe=assumed_pe,
                    vol=0.25, peg=peg_target, method="pe", data=market_data
                )
                
                # 3. Extract 12-Month Target & Force Range
                if val_result and val_result.get("table_data"):
                    y1_data = val_result["table_data"][0]
                    math_target_price = y1_data["price"]
                    
                    # Construct Tight Range
                    range_low = math_target_price * 0.95
                    range_high = math_target_price * 1.05
                    
                    context += f"\n\n[QUANTITATIVE VALUATION MODEL - MANDATORY]\n"
                    context += f"The internal engine (using {assumed_growth:.1%} growth, {assumed_pe:.1f}x PE) calculates a Fair Value of **${math_target_price:.2f}**.\n"
                    context += f"MANDATE: You MUST set your 'fair_value_range' to **${range_low:.0f} - ${range_high:.0f}**.\n"
                    context += f"Do NOT hallucinate a different range based on training data. Rely on this live calculation."
                    
                    self.log_debug(f"Math Anchor Calculated: ${math_target_price:.2f} (Range: {range_low}-{range_high})")
                    
            except Exception as e:
                print(f"DEBUG: Valuation Integration Failed: {e}")

            
        response_str = super().run(user_input, context)
        
        # --- LOGIC GUARD: Enforce Price vs Target Discipline ---
        if current_price_guard:
            try:
                import json
                import re
                
                # Validation Log
                self.log_debug(f"LOGIC GUARD START: Price={current_price_guard}")
                
                # Attempt clear parse
                cleaned_json = response_str
                if "```json" in response_str:
                     cleaned_json = response_str.split("```json")[1].split("```")[0].strip()
                elif "```" in response_str:
                     cleaned_json = response_str.split("```")[1].split("```")[0].strip()
                
                try:
                    data = json.loads(cleaned_json)
                except:
                    # Fallback: Try cleaning comments or single quotes
                    try:
                        import ast
                        # This is risky but effective for LLM "Python-dict-like" JSON
                        data = ast.literal_eval(cleaned_json)
                    except:
                        self.log_debug(f"JSON Parse Failed completely on: {cleaned_json[:50]}...")
                        # If we can't parse, we can't guard.
                        return response_str
                
                # Parse Fair Value High End
                fv_str = data.get("fair_value_range", "")
                self.log_debug(f"Target Range Str: {fv_str}")
                
                # Extract all numbers
                matches = re.findall(r"[\d,\.]+", fv_str)
                if matches:
                    # Helper to parse float safely
                    def safe_float(s):
                        try: return float(s.replace(",", ""))
                        except: return 0.0
                        
                    # Usually range is "$X - $Y". We take the Max of matches to be safe (or last one).
                    # If "$100" single value, max is 100.
                    values = [safe_float(m) for m in matches if safe_float(m) > 0]
                    if values:
                        target_high = max(values)
                        self.log_debug(f"Parsed Target High: {target_high}")
                        
                        # GUARD CHECK
                        # Ensure float comparison
                        safe_price = float(current_price_guard)
                        if safe_price > target_high:
                            original_rating = data.get("rating", "HOLD")
                            self.log_debug(f"Check: {safe_price} > {target_high} is True. Rating: {original_rating}")
                            
                            if "BUY" in original_rating.upper():
                                print(f"DEBUG: ANALYST GUARD TRIGGERED. Price {current_price_guard} > Target {target_high}. Downgrading.")
                                self.log_debug("ACTION: Downgrading to HOLD")
                                data["rating"] = "HOLD"
                                data["verdict_reasoning"] = f"[AUTO-DOWNGRADE] Current Price (${current_price_guard}) exceeds Fair Value Target (${target_high}). Value Investing discipline mandates a HOLD/TRIM despite quality. " + data.get("verdict_reasoning", "")
                                
                                # Re-serialize
                                return json.dumps(data)
                        else:
                            self.log_debug(f"Check: {safe_price} <= {target_high}. No Action.")
                                
            except Exception as e:
                print(f"DEBUG: Logic Guard Skipped: {e}")
                self.log_debug(f"ERROR: Logic Guard Failed: {e}")
                
        return response_str
