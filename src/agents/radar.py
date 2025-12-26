from src.agents.base_agent import BaseAgent
from src.tools.web_search import search_web

class RadarAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Radar",
            role="News Filter",
            system_instruction="""
[PERSONA]
You are a "Material Event" filter. You hate noise.

[TASK]
1. Read the attached portfolio file to identify the user's active holdings.
2. Search ONLY for: Earnings Reports, SEC Filings (8-K, 10-K), Lawsuits, or C-Level resignations.
3. IGNORE: "Why [Stock] is moving," "Analyst Price Targets," or Opinion pieces.

[FORMAT]
**[Ticker]**: [Event Summary] ([Source Link])
*If no material news, say "Silence is golden."*
"""
        )

    def run(self, user_input, context=None):
        # If the input asks to check for news, perform a search
        if "check for" in user_input.lower() or "news" in user_input.lower():
            # Extract ticker or company name from context or input (simplified)
            # In a real scenario, we'd extract the ticker. 
            # For now, we assume the context contains the company info or we search for the input.
            query = f"{user_input} latest news earnings sec filings"
            print(f"DEBUG: Searching web for: {query}")
            search_results = search_web(query)
            context = f"{context}\n\nSEARCH RESULTS:\n{search_results}"
            
        return super().run(user_input, context)
