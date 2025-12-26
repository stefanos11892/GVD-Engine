
import asyncio
import json
import sys
import os

sys.path.append(os.getcwd())

from src.agents.analyst import AnalystAgent
from src.agents.risk_officer import RiskOfficerAgent
from src.agents.architect import ArchitectAgent
from src.utils.orchestrator import AgentOrchestrator

async def test_full_chain():
    print("--- Testing Full Intelligence Chain (Analyst -> Risk -> Architect) ---")
    
    # 1. Setup Context (Simulating Originator)
    originator_context = "I have identified a strong candidate: PayPal Holdings (PYPL). It is trading at a historic low valuation."
    print(f"Context: {originator_context}")
    
    # 2. Parallel Phase
    analyst = AnalystAgent()
    risk = RiskOfficerAgent()
    
    tasks = [
        (analyst, "Analyze this stock.", originator_context),
        (risk, "Stress test this trade.", originator_context)
    ]
    
    print("\n[ORCHESTRATOR] Running Parallel Agents...")
    results = await AgentOrchestrator.run_parallel(tasks)
    
    analyst_output = results["Analyst"]
    risk_output = results["RiskOfficer"]
    
    # 3. Architect Phase
    architect = ArchitectAgent()
    architect_context = f"Analyst Report:\n{analyst_output}\n\nRisk Report:\n{risk_output}"
    
    print("\n[ARCHITECT] Making Decision...")
    architect_output = await architect.run_async("Review and decide.", context=architect_context)
    
    print("\n[FINAL OUTPUT]")
    print(architect_output)
    
    # 4. Validation
    try:
        clean_json = architect_output.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_json)
        
        if "decision" in data and "allocation_size_percent" in data:
             print(f"\n[SUCCESS] Architect produced valid JSON decision: {data['decision']} @ {data['allocation_size_percent']}")
        else:
             print("\n[FAILED] Architect JSON missing required keys.")
             sys.exit(1)
             
    except json.JSONDecodeError as e:
        print(f"\n[FAILED] Architect Output is not JSON. {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_full_chain())
