from src.agents.base_agent import BaseAgent
from typing import Dict, Any
import json
import logging

logger = logging.getLogger("QualAgent")

class QualAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Qual Agent (The Anthropologist)",
            role="Narrative Analyst",
            system_instruction="""
[SYSTEM: QUALITATIVE ANALYST]
ROLE: You are an expert anthropologist studying Corporate Management Teams.
GOAL: Decode the "Narrative Tone" and hidden signals in the text.
OUTPUT: JSON conforming to the Qualitative Schema.

ANALYSIS FRAMEWORK:
1.  **Sentiment**: Is the tone effectively Bullish, Bearish, or Neutral?
2.  **Vagueness Detection**: Flag phrasing that sounds defensive or evasive (e.g., "headwinds", "challenging environment", "transition year").
3.  **Confidence**: How confident is management in their own projections?

JSON SCHEMA:
{
  "sentiment_score": 0.0 to 1.0 (0=Bearish, 1=Bullish),
  "narrative_tone": "Bullish" | "Bearish" | "Neutral" | "Defensive",
  "key_themes": ["Efficiency", "Growth", "Cost Cutting"],
  "vagueness_flags": [
    "Used term 'headwinds' 5 times",
    "Avoided direct answer on Q4 guidance"
  ],
  "management_confidence": "High" | "Medium" | "Low"
}
"""
        )

    def analyze_sentiment(self, text_segment: str) -> Dict[str, Any]:
        """
        Analyzes the sentiment and narrative tone of a text segment.
        """
        prompt = f"""
TASK: Analyze the following Management Discussion snippet.

TEXT:
\"\"\"
{text_segment[:10000]}
\"\"\"

INSTRUCTIONS:
- Ignore specific numbers (that's the Quant's job).
- Focus on adjectives, qualifiers, and sentence structure.
- Return valid JSON only.
"""
        response = self.run(prompt)
        
        try:
             # Basic JSON Extraction
            if "{" in response and "}" in response:
                json_str = response[response.find("{"):response.rfind("}")+1]
                data = json.loads(json_str)
                return data
            else:
                return {"error": "No JSON found in Qual response", "raw": response}
        except Exception as e:
            logger.error(f"Qual Analysis Failed: {e}")
            return {"error": str(e), "raw": response}
