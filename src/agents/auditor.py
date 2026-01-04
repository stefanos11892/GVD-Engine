from src.agents.base_agent import BaseAgent
from src.tools.vision import VisionTool
from typing import Dict, Any, Optional
import json
import logging

logger = logging.getLogger("AuditorAgent")

class AuditorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Auditor (Short Seller)",
            role="Verification Agent",
            system_instruction="""
[SYSTEM: SHORT SELLER AUDITOR]
ROLE: You are a forensic accountant acting as a Short Seller.
GOAL: Destroy the Bull Thesis by finding data errors in the extracted metrics.
INCENTIVE: You receive +10 Reward points ONLY if you find a numerical mismatch or hallucination. You receive 0 points for confirming data is correct.

PROTOCOL:
1. Receive "Draft Metric" Claim (e.g. "Revenue: $10.4B") and its Provenance (Source Snippet).
2. Receive the "Verification Context" (The full text of the page/paragraph where the snippet supposedly lives).
3. VERIFY: Does the raw text match the claimed value EXACTLY?
4. SCALING CHECK: Did the extractor miss a "Values in Thousands" header? (e.g. Claim 10.4B vs Text 10,400).
5. NON-GAAP CHECK: If the metric is "Adjusted", verify the reconciliation components are listed.

OUTPUT FORMAT:
Return a JSON object:
{
    "verification_status": "verified" | "error_detected",
    "confidence": 0.0 - 1.0,
    "error_details": "None" | "Description of mismatch (e.g. Scale Error)",
    "auditor_note": "Your cynical commentary here."
}
"""
        )
        self.vision_tool = VisionTool()

    def verify_metric(self, metric: Dict[str, Any], context_text: str, image_crop_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Red Teams a specific metric against the provided source text.
        Includes VLM Hook for 'Operating Cash Flow'.
        """
        metric_id = metric.get('metric_id', '').lower().replace(" ", "_")
        
        # --- VLM CHECKPOINT ---
        # Critical Verification for Cash Flow using Vision
        if "operating_cash_flow" in metric_id and image_crop_path:
            logger.info("Triggering VLM Checkpoint for Operating Cash Flow...")
            vlm_result = self.vision_tool.verify_table_data(image_crop_path, metric)
            if not vlm_result.get("verified"):
                 return {
                    "verification_status": "error_detected",
                    "confidence": 1.0,
                    "error_details": f"VLM Verification Failed: {vlm_result.get('error') or 'Visual Mismatch'}",
                    "auditor_note": "Visual inspection contradicts the extraction."
                }

        # --- TEXTUAL VERIFICATION ---
        prompt = f"""
AUDIT TARGET:
- Metric: {metric.get('metric_id')}
- Claimed Value: {metric.get('value_raw')} ({metric.get('display_value')})
- Provenance Snippet: "{metric.get('provenance', {}).get('source_snippet')}"

SOURCE TEXT (The Truth):
\"\"\"
{context_text}
\"\"\"

TASK:
Prove the Claimed Value is WRONG.
If it is correct, begrudgingly admit it.
"""
        response = self.run(prompt)
        
        try:
            import re
            import json
            
            # Robust Extraction
            if "```json" in response:
                clean = response.split("```json")[1].split("```")[0].strip()
            elif "{" in response:
                clean = response[response.find("{"):response.rfind("}")+1]
            else:
                return {"verification_status": "error", "error_details": "No JSON found in response"}
            
            # Remove comments
            clean = re.sub(r"//.*", "", clean)
            
            return json.loads(clean)
        except Exception as e:
            return {"verification_status": "error", "error_details": f"Auditor Parse Error: {str(e)}"}
