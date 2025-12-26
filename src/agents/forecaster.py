from src.agents.base_agent import BaseAgent
from src.tools.web_search import search_web

class ForecasterAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Forecaster",
            role="FP&A Director",
            system_instruction="""
Role: Expert Quantitative Financial Analyst and FP&A Director.
Objective: Analyze the company and provide Key Financial Assumptions for a Monte Carlo Simulation.
Output Format: Strict JSON. Do NOT generate HTML.

JSON Structure:
{
  "ticker": "AAPL",
  "current_price": 150.0,
  "metrics": {
      "revenue": "383.9B",
      "net_income": "96.9B"
  },
  "base_case": {
    "revenue_growth": 0.15,  // 15%
    "target_net_margin": 0.25, // 25%
    "target_pe": 25.0,
    "volatility": 0.30 // Annualized Std Dev
  },
  "bear_case": {
    "revenue_growth": 0.05,
    "target_net_margin": 0.15,
    "target_pe": 15.0
  },
  "bull_case": {
    "revenue_growth": 0.25,
    "target_net_margin": 0.30,
    "target_pe": 35.0
  },
  "rationale": "Detailed reasoning for these assumptions..."
}
"""
        )

    def run(self, user_input, context=None):
        # 1. Detect Ticker
        ticker = None
        words = user_input.split()
        for word in words:
            if word.isupper() and len(word) <= 5:
                ticker = word
                break
        
        if ticker:
            print(f"DEBUG: Forecaster identified ticker: {ticker}")
            
            # 2. Fetch Data via Local Market Data Tool (Reliable)
            from src.tools.market_data import get_market_data
            data = get_market_data(ticker)
            print(f"DEBUG: Forecaster Market Data: {data}")
            
            # 3. Augment Context
            context = f"""
            Task: Use the following REAL-TIME financial data for {ticker} to populates the JSON. 
            Do NOT search the web. Use these EXACT numbers from the dictionary below.
            
            MARKET DATA DICTIONARY:
            {data}
            
            CRITICAL INSTRUCTIONS:
            1. Set "current_price" to {data.get('price')}.
            2. Set "metrics.revenue" to {data.get('revenue_ttm')} (Format nicely, e.g. "2.3B").
            3. Set "metrics.net_income" to {data.get('net_income_ttm')} (Format nicely).
            4. If 'volatility' is None, use Beta {data.get('beta')} to estimate (Beta > 1.5 = High Volatility > 40%).
            """
        
        response = super().run(user_input, context)
        
        # Post-Process: Force Real Data into JSON (Prevent Hallucination)
        try:
            import json
            import re
            
            # Extract JSON from response
            json_str = response
            match = re.search(r"```json\s*(\{.*?\})\s*```", response, re.DOTALL)
            if match:
                 json_str = match.group(1)
            elif "```" in response:
                 match = re.search(r"```\s*(\{.*?\})\s*```", response, re.DOTALL)
                 if match: json_str = match.group(1)
            else:
                 # Try finding braces
                 start = response.find("{")
                 end = response.rfind("}")
                 if start != -1 and end != -1:
                    json_str = response[start:end+1]

            agent_data = json.loads(json_str)
            
            # OVERWRITE with Real Data
            agent_data["current_price"] = data.get("price")
            
            # Helper to format big numbers
            def fmt(n):
                if not n: return "N/A"
                if n > 1e9: return f"{n/1e9:.2f}B"
                if n > 1e6: return f"{n/1e6:.2f}M"
                return str(n)

            if "metrics" not in agent_data: agent_data["metrics"] = {}
            agent_data["metrics"]["revenue"] = fmt(data.get("revenue_ttm"))
            agent_data["metrics"]["net_income"] = fmt(data.get("net_income_ttm"))
            
            # Recalculate Volatility if missing
            if not agent_data.get("base_case", {}).get("volatility"):
                 val = data.get("volatility")
                 if not val: val = 0.35 # Default
                 if "base_case" not in agent_data: agent_data["base_case"] = {}
                 agent_data["base_case"]["volatility"] = val

            return json.dumps(agent_data, indent=2)
            
        except Exception as e:
            print(f"DEBUG: Failed to post-process agent JSON: {e}")
            return response

