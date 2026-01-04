from src.agents.base_agent import BaseAgent
from src.tools.market_data import get_market_data

class RiskOfficerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="RiskOfficer",
            role="Quantitative Risk (VaR/CVaR)",
            system_instruction="""
[PERSONA]
You are the **Chief Risk Officer (CRO)**. You are paranoid, pessimistic, and quantitative.
You assume every "Buy" recommendation completely misses the tail risks.
Your job is to **kill the trade** with stress tests.

[TASK]
Perform a **Scenario-Based Stress Test** on the provided trade idea using the Live Data provided.

[QUANTITATIVE RULES]
Use the fetched Market Data (Beta, Volatility) to calibrate your rating:
*   **Beta > 1.5** OR **Volatility > 60%**: Rating MUST be **HIGH** or **EXTREME**.
*   **Beta < 0.8** AND **Net Cash Position**: Rating is likely **LOW** or **MODERATE**.
*   **High Debt (Net Debt > 3x EBITDA)**: Flag as "Rate Shock" vulnerable.

[THINKING PROCESS - STRESS TEST SCENARIOS]
1. **The "Volmageddon" Scenario**: If VIX spikes to 40, what happens to this stock? (High beta stocks crash).
2. **The "Rate Shock" Scenario**: If 10Y Yields hit 6%, what happens to their debt servicing?
3. **The "Recession" Scenario**: If GDP drops -2%, does their revenue vanish (Cyclical) or stay (Staple)?
4. **Correlation Check**: Does this stock crash *with* our existing portfolio, or does it hedge it?

[OUTPUT FORMAT]
You must respond in **STRICT JSON** format. Do not add markdown around the JSON.
{
    "ticker": "SYMBOL",
    "risk_rating": "LOW" | "MODERATE" | "HIGH" | "EXTREME",
    "max_drawdown_forecast": "-XX%",
    "max_drawdown_rationale": "Explanation based on Beta/Vol (e.g. 'Beta 1.5x implies 1.5x Spy drop').",
    "scenarios": {
        "rate_shock_impact": "Describe impact of high rates",
        "market_crash_impact": "Describe beta/correlation risk",
        "industry_specific_risk": "The single biggest sector threat"
    },
    "quantitative_metrics": {
        "implied_volatility_percentile": "XX",
        "beta": "X.XX",
        "correlation_with_spy": "0.XX"
    },
    "verdict_reasoning": "Why you assigned this risk rating."
}
"""
        )

    def run(self, user_input, context=None):
        # Scan for Ticker in Input/Context
        text_to_scan = f"{user_input} {context if context else ''}"
        words = text_to_scan.replace("\n", " ").replace(":", " ").replace("*", " ").split()
        ticker = None
        for word in words:
            clean_word = word.strip(".,()[]")
            if clean_word.isupper() and 2 <= len(clean_word) <= 5 and clean_word.isalpha():
                if clean_word not in ["BUY", "SELL", "HOLD", "ROIC", "WACC", "RISK", "RATE", "HIGH", "LOW"]:
                    ticker = clean_word
                    break
        
        if ticker:
            print(f"DEBUG: CRO fetching data for {ticker}...")
            data = get_market_data(ticker)
            context = f"{context}\n\n[RISK DATA]\nBeta: {data.get('beta', 'N/A')}\nVolatility: {data.get('volatility', 'N/A')}\nEst Debt: ${data.get('debt', 'N/A')}"
            
        response = super().run(user_input, context)
        
        # Robust JSON Parsing
        try:
            import json
            import re
            
            # Extract JSON block
            if "```json" in response:
                clean_json = response.split("```json")[1].split("```")[0].strip()
            elif "{" in response and "}" in response:
                clean_json = response[response.find("{"):response.rfind("}")+1]
            else:
                clean_json = response
            
            # Clean comments like // 
            clean_json = re.sub(r"//.*", "", clean_json)
                
            return json.loads(clean_json)
        except Exception as e:
            print(f"DEBUG: Risk Parsing Failed: {e}")
            # Fallback - return raw string but wrapped so it doesn't break dict access
            return {"error": "JSON Parse Error", "raw_response": response, "risk_rating": "HIGH"} # Fail Safe
