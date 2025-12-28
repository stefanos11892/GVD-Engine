from src.agents.base_agent import BaseAgent
from typing import Dict, Any, List
import json
import logging
from datetime import datetime

logger = logging.getLogger("ConsolidatorAgent")

class ConsolidatorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Consolidator (Portfolio Manager)",
            role="Thesis Synthesizer",
            system_instruction="""
[SYSTEM: CONSOLIDATOR]
ROLE: You are a Portfolio Manager synthesizing analyst reports to form a final Institutional Thesis.
GOAL: Identify "Friction" between the Narrative (Qual) and the Data (Quant).
OUTPUT: A consolidated Institutional Report JSON.

LOGIC:
1.  **Thesis Friction**: Compare the "Narrative Tone" with "Metric Trends".
    *   IF Tone="Bullish" AND Revenue="Declining" -> FLAG FRICTION ("Management Denial").
    *   IF Tone="Bearish" AND Revenue="Growing" -> FLAG FRICTION ("Sandbagging").
2.  **Conviction Score**: 
    *   0.0 - 0.4: High Friction / Contradictory Signals.
    *   0.5 - 0.7: Mixed Signals.
    *   0.8 - 1.0: High Alignment (Data matches Narrative).

3.  **Delta Integration**: Incorporate "Silent Omissions" and "Retreats" as Risk Factors.

JSON SCHEMA:
{
  "institutional_thesis": "Bullish/Bearish/Neutral Statement",
  "conviction_score": 0.85,
  "friction_analysis": [
    {
       "type": "Tone vs Data", 
       "description": "Management is selling growth, but Revenue is down 5%."
    }
  ],
  "key_risks": ["Silent Omission: Crypto Risk", "Numerical Retreat: Gross Margin"],
  "final_verdict": "Buy/Sell/Hold"
}
"""
        )

    def synthesize_report(
        self, 
        quant_data: Dict[str, Any], 
        qual_data: Dict[str, Any], 
        delta_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Synthesizes the final report from the three streams.
        """
        # Construct a Context Prompt for the LLM
        context = f"""
ANALYST REPORTS:

1. QUANT (HARD DATA):
{json.dumps(quant_data, indent=2)}

2. QUAL (NARRATIVE):
{json.dumps(qual_data, indent=2)}

3. DELTA (CONTEXT SHIFTS):
{json.dumps(delta_data, indent=2)}

TASK:
- Identify contradictions (Friction).
- Assign Conviction Score (0.0-1.0).
- Produce Final Verdict.
"""
        response = self.run(context)
        
        try:
             # Basic JSON Extraction
            if "{" in response and "}" in response:
                json_str = response[response.find("{"):response.rfind("}")+1]
                data = json.loads(json_str)
                return data
            else:
                return {"error": "No JSON found in Consolidator response", "raw": response}
        except Exception as e:
            logger.error(f"Consolidation Failed: {e}")
            return {"error": str(e), "raw": response}
