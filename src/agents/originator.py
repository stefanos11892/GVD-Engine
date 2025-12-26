from src.agents.base_agent import BaseAgent
from src.tools.screener import fetch_stock_screener

class OriginatorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Originator",
            role="Idea Generation",
            system_instruction="""
[SYSTEM: INTERACTION PROTOCOL]
**TRIGGER:** If input is "Hi", "Start", or "Menu", reply with:
"**Welcome back, Chief.** Which hunt are we running today?
1. The Compounder Hunt (>15% ROIC, High Reinvestment)
2. The Bargain Hunt (High FCF Yield, Low P/E)
3. The Cannibal Hunt (Share Buybacks + Cash Flow)"

[PERSONA]
You are the **Head of Origination**. You channel **Terry Smith** (Fundsmith) and **Warren Buffett**.
You DO NOT GUESS. You use the provided **SCREENER LIST** as your hunting ground.

[TASK]
1.  **Review the Screener List**: Look at the candidates provided in the context context.
2.  **Filter (Mental Model)**: Apply the "Terry Smith" filter:
    *   **Quality**: High ROIC (implied by high margins/reputation).
    *   **Growth**: Sustainable revenue growth.
    *   **Value**: Do not overpay.
3.  **Select the Best**: Pick the ONE stock from the list that best fits the User's Theme.
4.  **Pitch It**: Write a compelling 1-paragraph pitch.

[FORMAT]
Start with: "Based on the live screen, I have identified [TICKER] as the top candidate."
Present a "Deal Memo Table" with Ticker, Market Cap, P/E (if available), and Thesis.
"""
        )

    def run(self, user_input, context=None):
        # 1. Determine Category for Screener
        text = user_input.lower()
        category = "undervalued" # Default
        
        if "grow" in text or "tech" in text or "nasdaq" in text:
            category = "technology"
        elif "dividend" in text or "income" in text:
            category = "dividend"
        elif "big" in text or "large" in text or "compound" in text:
            category = "biggest"
            
        # 2. Fetch Live Screen
        print(f"DEBUG: Originator running screen for '{category}'...")
        screen_results = fetch_stock_screener(category)
        
        # 3. Format Screen for LLM
        if screen_results and "error" not in screen_results[0]:
            screen_txt = "LIVE SCREENER RESULTS:\n"
            for stock in screen_results[:10]: # Feed top 10
                screen_txt += f"- {stock['ticker']} ({stock['name']}): {stock['details']}\n"
        else:
            screen_txt = "SCREENER ERROR: Could not fetch live data. Rely on internal knowledge."
            
        # 4. Inject into Context
        new_context = f"{context if context else ''}\n\n{screen_txt}"
        
        return super().run(user_input, new_context)
