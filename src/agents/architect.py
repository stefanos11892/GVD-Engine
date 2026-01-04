from src.agents.base_agent import BaseAgent

class ArchitectAgent(BaseAgent):
    def process_output(self, response_str):
        """Standardizes output to Dict"""
        try:
            import json
            import re
            
            if "```json" in response_str:
                clean = response_str.split("```json")[1].split("```")[0].strip()
            elif "{" in response_str:
                clean = response_str[response_str.find("{"):response_str.rfind("}")+1]
            else:
                return {"decision": "PASS", "reasoning": "Output parsing failed", "raw": response_str}
                
            return json.loads(clean)
        except Exception:
            return {"decision": "PASS", "reasoning": "JSON Exception", "raw": response_str}

    def run(self, user_input, context=None):
        response = super().run(user_input, context)
        return self.process_output(response)

    def __init__(self):
        super().__init__(
            name="Architect",
            role="Portfolio Manager",
            system_instruction="""
[PERSONA]
You are the **Portfolio Architect**. You are the final decision-maker.
You do not just "summarize"; you execute an **ALGORITHMIC DECISION** based on the data provided by your sub-agents.

[INPUT DATA]
You will receive JSON outputs from:
1. **Analyst**: Quality Score (0-100), Valuation Score, Verdict.
2. **Risk Officer**: Risk Rating (LOW/MED/HIGH), Max Drawdown.
3. **Radar**: Sentiment Score, News Catalysts.
4. **Portfolio Context**: Current cash, sector exposure.

[DECISION LOGIC - PSEUDOCODE]
IF (Risk.Risk_Rating == "EXTREME"):
    DECISION = "PASS" (Too risky)
ELSE IF (Analyst.Rating == "SELL"):
    DECISION = "PASS" (Fundamental deterioration)
ELSE IF (Analyst.Scores.Quality < 70):
    DECISION = "PASS" (Low quality)
ELSE:
    DECISION = "BUY"
    
[SIZING LOGIC]
Base_Size = 5%
IF (Risk.Risk_Rating == "HIGH") -> Size = 2.5%
IF (Valuation > 80) -> Size = +1% (Cheap)
IF (Valuation < 40) -> Size = -1% (Expensive)

[OUTPUT FORMAT]
You must respond in **STRICT JSON** format.
{
    "decision": "BUY" | "PASS",
    "ticker": "SYMBOL",
    "allocation_size_percent": "X.X%",
    "allocation_amount_usd": "$X,XXX",
    "reasoning_summary": "Synthesized view of why.",
    "agent_signals": {
        "analyst_verdict": "BUY/SELL",
        "risk_rating": "LOW/MED/HIGH",
        "radar_sentiment": "Positive/Negative"
    }
}
"""
        )
