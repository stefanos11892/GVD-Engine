import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, List

from src.parsers.financial_pdf import FinancialPDFParser
from src.agents.quant import QuantAgent
from src.agents.auditor import AuditorAgent
from src.agents.auditor_logic import CoordinateVerifier
from src.agents.qual import QualAgent
from src.agents.consolidator import ConsolidatorAgent

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EarningsAuditWorkflow")

class EarningsAuditOrchestrator:
    def __init__(self):
        self.parser = FinancialPDFParser()
        self.quant = QuantAgent()
        self.qual = QualAgent()
        self.consolidator = ConsolidatorAgent()
        self.auditor = AuditorAgent()
        self.coord_verifier = CoordinateVerifier()
        self.log_history = []

    async def run_workflow(self, pdf_path: str) -> Dict[str, Any]:
        """
        Executes the full Institutional Earnings Workflow with One-Strike Recovery.
        """
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        logger.info(f"--- Starting Audit Run {run_id} for {pdf_path} ---")

        # 1. PARSE (Foundation)
        parse_result = self.parser.parse(pdf_path)
        markdown = parse_result["markdown"]
        
        # 2. EXTRACT (Quant)
        logger.info("Asking Quant Agent to extract metrics (Attempt 1)...")
        quant_result = self.quant.extract_metrics(markdown)
        
        if "error" in quant_result:
             logger.error("Quant failed to produce JSON.")
             return {"status": "failed", "step": "quant_extraction"}

        metrics = quant_result.get("metrics", [])
        verified_metrics = []
        
        # 3. VERIFICATION & RECOVERY LOOP
        for metric in metrics:
            metric_id = metric.get('metric_id')
            logger.info(f"Verifying: {metric_id} ({metric.get('value_raw')})")
            
            # --- ATTEMPT 1 ---
            audit_result = await self.verify_single_metric(metric, pdf_path)
            
            if audit_result["status"] == "error_detected":
                logger.warning(f"Detection! {audit_result.get('note')}")
                
                # --- RECOVERY (ATTEMPT 2) ---
                logger.info(f"Attempting One-Strike Recovery for {metric_id}...")
                feedback = f"Error in {metric_id}: {audit_result.get('note')}. {audit_result.get('details')}"
                
                # Re-query Quant with Feedback
                retry_output = self.quant.extract_metrics(markdown, target_metrics=[metric_id], feedback=feedback)
                
                # Extract corrected metric from response
                corrected_metrics = retry_output.get("metrics", [])
                corrected_metric = next((m for m in corrected_metrics if m.get("metric_id") == metric_id), None)
                
                if corrected_metric:
                    logger.info(f"Quant provided correction: {corrected_metric.get('value_raw')}")
                    # Re-Verify
                    audit_result_2 = await self.verify_single_metric(corrected_metric, pdf_path)
                    
                    if audit_result_2["status"] == "verified":
                         logger.info(f"Recovery Successful for {metric_id}")
                         corrected_metric["verification"] = audit_result_2
                         corrected_metric["recovery_used"] = True
                         
                         # CHAIN OF FAILURE (Institutional Grade Transparency)
                         # We record the original sin so analysts know the risk.
                         corrected_metric["audit_history"] = [
                             {
                                 "attempt": 1,
                                 "value_raw": metric.get("value_raw"),
                                 "verification": audit_result,
                                 "timestamp": datetime.now().isoformat()
                             }
                         ]
                         
                         verified_metrics.append(corrected_metric)
                         self.log_history.append({"metric_id": metric_id, "status": "Recovered", "details": feedback})
                    else:
                         # FINAL FAIL
                         logger.error(f"Recovery Failed for {metric_id}. Escalating to Human Review.")
                         metric["verification"] = audit_result_2
                         metric["flagged"] = True
                         metric["intervention_required"] = True
                         metric["failure_chain"] = [audit_result, audit_result_2]
                         self.log_history.append({"metric_id": metric_id, "status": "Failed", "chain":metric["failure_chain"]})
                         verified_metrics.append(metric) # Append broken metric for review
                else:
                    logger.error(f"Quant failed to provide correction for {metric_id}.")
                    metric["verification"] = audit_result
                    metric["flagged"] = True
                    verified_metrics.append(metric)

            else:
                # Pass
                metric["verification"] = audit_result
                metric["flagged"] = False
                verified_metrics.append(metric)
                self.log_history.append({"metric_id": metric_id, "status": "Verified"})

        # 4. QUALITATIVE ANALYSIS (The Anthropologist)
        logger.info("Asking Qual Agent to analyze sentiment...")
        qual_result = self.qual.analyze_sentiment(markdown)
        
        # 5. THESIS CONSOLIDATION (The Portfolio Manager)
        logger.info("Synthesizing Institutional Thesis...")
        
        # Prepare data for Consolidator
        quant_summary = {m['metric_id']: m.get('value_raw') for m in verified_metrics}
        
        thesis_result = self.consolidator.synthesize_report(
            quant_data=quant_summary,
            qual_data=qual_result,
            delta_data={"notes": "No historical delta available yet."} 
        )

        # 6. FINALIZE
        final_report = {
            "run_id": run_id,
            "timestamp": datetime.now().isoformat(),
            "pdf_path": pdf_path,
            "metrics": verified_metrics,
            "qual_analysis": qual_result,
            "institutional_thesis": thesis_result,
            "quant_note": quant_result.get("note"),
            "quant_error": quant_result.get("error")
        }
        
        # 5. AUDIT LOGGING
        self.save_log(final_report)
        return final_report

    async def verify_single_metric(self, metric: Dict[str, Any], pdf_path: str) -> Dict[str, Any]:
        """
        The Verification Triad: Physical, Logic, Vision.
        """
        provenance = metric.get("provenance", {})
        bbox = provenance.get("bbox")
        page = provenance.get("page")
        snippet = provenance.get("source_snippet")
        
        # A. PHYSICAL CHECK (Coordinate JUMP)
        if bbox and page:
            jump_check = self.coord_verifier.verify_jump(pdf_path, page, bbox, metric.get("value_raw"))
            if not jump_check["match"]:
                 return {
                    "status": "error_detected",
                    "reason": "Coordinate JUMP Mismatch",
                    "note": f"Text at coordinates is '{jump_check.get('ground_truth_text')}', not '{metric.get('value_raw')}'",
                    "details": "PyMuPDF Physical Validation Failed"
                }

        # B. LOGIC & VISION CHECK (Auditor Agent)
        context_text = snippet 
        audit_response = self.auditor.verify_metric(metric, context_text)
        
        return {
            "status": audit_response.get("verification_status", "unknown"),
            "note": audit_response.get("auditor_note", ""),
            "details": audit_response.get("error_details", "")
        }

    def save_log(self, report):
        log_file = "verification_log.json"
        try:
            with open(log_file, "w") as f:
                json.dump(report, f, indent=2)
            logger.info(f"Audit Log saved to {log_file}")
            
            # Save chain of events logs too if needed, but report has the history
        except Exception as e:
            logger.error(f"Failed to save log: {e}")

if __name__ == "__main__":
    # Test Stub
    orchestrator = EarningsAuditOrchestrator()
    print("Orchestrator Factory Loaded.")
