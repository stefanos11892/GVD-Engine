from src.agents.base_agent import BaseAgent
from typing import Dict, Any, List
import json
import logging

logger = logging.getLogger("QuantAgent")

class QuantAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Quant Agent (Miner)",
            role="Financial Extraction Specialist",
            system_instruction="""
[SYSTEM: QUANT AGENT (THE SKEPTIC)]
ROLE: You are an expert financial data specialist acting as a SKEPTIC.
GOAL: Extract precise hard data (GAAP/Non-GAAP) and IGNORE all management narrative.

RULES:
1.  **DATA ONLY**: Do not extract "feelings", "beliefs", or "expectations" unless backed by a hard number range.
2.  **IGNORE SPIN**: If management says "Strong growth of 5%", you extract "Revenue Growth: 5%". You DO NOT extract "Strong".
3.  **PROVENANCE**: Every metric MUST include a 'provenance' object with the source text snippet.
4.  **EXACTNESS**: Extract exact values (e.g. 10.4B). Do not round.

JSON SCHEMA:
{
  "metrics": [
    {
      "metric_id": "standardized_id",
      "display_name": "Revenue",
      "value_raw": "10.4B",
      "provenance": {
        "source_snippet": "Total Revenue ... $10.4B",
        "page": 45
      }
    }
  ],
  "note": "Optional explanation if data is missing or incorporated by reference."
}
"""
        )

    def extract_metrics(self, markdown_content: str, target_metrics: List[str] = None, feedback: str = None) -> Dict[str, Any]:
        """
        Extracts specific metrics from the Markdown content.
        
        Uses RAG (Retrieval-Augmented Generation) to select only relevant
        sections instead of dumping the entire 500k character document.
        
        Supports Feedback Injection for One-Strike Recovery.
        """
        # Default metrics if none specified
        default_metrics = ["Revenue", "Net Income", "EBITDA", "Operating Cash Flow", "EPS"]
        metrics_list = target_metrics if target_metrics else default_metrics
        target_str = ", ".join(metrics_list)
        
        # ======================================
        # RAG: RETRIEVE RELEVANT CONTEXT
        # ======================================
        # Instead of passing 500k chars, retrieve only relevant sections
        try:
            from src.utils.rag import get_context_for_metrics
            relevant_context = get_context_for_metrics(
                metrics=metrics_list,
                markdown=markdown_content,
                max_chars=25000  # ~25k chars vs 500k = 95% reduction
            )
            logger.info(f"RAG retrieved {len(relevant_context)} chars (reduced from {len(markdown_content)})")
        except ImportError:
            # Fallback if RAG dependencies not installed
            logger.warning("RAG not available, using truncated context")
            relevant_context = markdown_content[:50000]
        except Exception as e:
            logger.warning(f"RAG failed: {e}, using fallback")
            relevant_context = markdown_content[:50000]
        
        feedback_prompt = ""
        if feedback:
            feedback_prompt = f"""
CRITICAL CORRECTION REQUEST:
Your previous extraction was REJECTED by the Auditor.
Auditor Feedback: "{feedback}"
CONSTRAINT: You must fix this specific error. Do not repeat the same mistake.
"""

        prompt = f"""
TASK: Extract the following metrics: {target_str}.

{feedback_prompt}

DOCUMENT CONTEXT (Retrieved Sections):
\"\"\"
{relevant_context}
\"\"\"
(Note: These are the most relevant sections for your task, retrieved via semantic search.)

INSTRUCTIONS:
- Find the most recent annual data (Current Year).
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
                return {"error": "No JSON found in Quant response", "raw": response}
        except Exception as e:
            logger.error(f"Quant Extraction Failed: {e}")
            return {"error": str(e), "raw": response}
