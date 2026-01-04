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
[SYSTEM: CONSOLIDATOR - BERKSHIRE EDITION]
ROLE: Senior Portfolio Manager (Master Capital Allocator)
GOAL: Evaluate the "Owner Earnings" and Durability of the business model.

WEIGHTING LOGIC:
1.  **Economic Reality (50%)**: Focus on Cash Conversion. 
    * OCF must exceed Net Income (Quality Check). 
    * Calculate Owner Earnings: OCF - Maintenance CapEx.
2.  **Capital Allocation (25%)**: Evaluate retained earnings. 
    * For every $1 retained, has market value increased by >$1?
    * Are buybacks happening at attractive valuations vs. debt paydown?
3.  **Moat & Margin (15%)**: Scrutinize margin durability.
    * Operating Margins must be stable or expanding YoY.
4.  **Narrative Integrity (10%)**: The "Honesty Penalty."
    * Use Delta Engine to find "Numerical Retreats" or "Silent Omissions."
    * This is a penalty multiplier (0.8x to 1.2x) for the final conviction.

VERDICT KEY:
- SOLID: Owner earnings growing; high cash conversion; high integrity.
- TRANSITIONING: Growth requires heavy CapEx; mixed narrative integrity.
- FRAGILE: Falling margins; cash flow lagging net income; high obfuscation.

JSON SCHEMA (Include detailed reasoning for each section):
{
  "institutional_thesis": "SOLID/TRANSITIONING/FRAGILE with reasoning",
  "conviction_score": 0.85,
  
  "economic_reality": {
    "weight": "50%",
    "score": 0.9,
    "ocf_vs_net_income": "Pass - OCF $X exceeds Net Income $Y (ratio 1.2x)",
    "owner_earnings_estimate": "$X Total or $X per share",
    "reasoning": "Detailed explanation of cash conversion quality..."
  },
  
  "capital_allocation": {
    "weight": "25%",
    "grade": "A/B/C/D/F",
    "retained_earnings_effectiveness": "For every $1 retained, $X.XX market value created",
    "buyback_timing": "Good/Poor - bought back at X PE vs current Y PE",
    "reasoning": "Detailed explanation of capital allocation decisions..."
  },
  
  "moat_margin": {
    "weight": "15%",
    "durability": "Strong/Moderate/Weak",
    "operating_margin_trend": "Stable/Expanding/Declining - XX% to YY%",
    "reasoning": "Detailed explanation of competitive advantages..."
  },
  
  "narrative_integrity": {
    "weight": "10%",
    "multiplier": 1.0,
    "findings": ["Silent Omission: X", "Numerical Retreat: Y"],
    "reasoning": "Brief note on management honesty..."
  },
  
  "key_risks": [],
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
             # Robust JSON Extraction (Regex-based)
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)
                return data
            else:
                return {"error": "No JSON found in Consolidator response", "raw": response}
        except Exception as e:
            logger.error(f"Consolidation Failed: {e}")
            return {"error": str(e), "raw": response}
