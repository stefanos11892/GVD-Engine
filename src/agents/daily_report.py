from src.agents.base_agent import BaseAgent
from src.tools.web_search import search_web

class DailyReportAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="DailyReport",
            role="Market Analyst",
            system_instruction="""
[CAPABILITIES]
You have access to a Knowledge file named "factor_analysis_sop.md".

[TRIGGER]
Whenever the user asks for a "Factor Report" or "Market Analysis," perform these steps:
1. READ THE SOP: Refresh memory on logic.
2. EXECUTE PHASE 1: Search web for prices/percentages in SOP.
3. EXECUTE PHASE 2: Use Python to calculate Factor Scores.
4. REPORT: Output final analysis based on Phase 3 logic.
"""
        )

    def run(self, user_input, context=None):
        if "report" in user_input.lower() or "analysis" in user_input.lower():
            print("DEBUG: Gathering market data for Daily Report...")
            # Search for the indices mentioned in the SOP
            query = "current price change SPY QQQ IWM VIX 10-year treasury yield"
            search_results = search_web(query)
            context = f"{context}\n\nMARKET DATA:\n{search_results}"
            
        return super().run(user_input, context)
