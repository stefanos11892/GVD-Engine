from src.agents.originator import OriginatorAgent
from src.agents.analyst import AnalystAgent
from src.agents.risk_officer import RiskOfficerAgent
from src.agents.architect import ArchitectAgent

def run_new_idea_chain(user_input):
    logs = []
    def log(msg):
        # Sanitize for Windows Console compatibility
        safe_msg = str(msg).encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
        try:
            print(safe_msg)
        except Exception:
            # Fallback if print still fails
            pass
        logs.append(safe_msg)

    log("--- Starting Workflow A: The 'New Idea' Chain ---")
    
    # 1. Originator
    originator = OriginatorAgent()
    log("\n[1/4] @Originator is generating ideas...")
    originator_output = originator.run(user_input)
    log(f"Originator Output:\n{originator_output}\n")
    
    # --- PARALLEL PHASE ---
    import asyncio
    from src.utils.orchestrator import AgentOrchestrator
    
    log("\n[2/4] @Orchestrator is spawning parallel agents (Analyst, Risk, Radar)...")
    
    analyst = AnalystAgent()
    risk_officer = RiskOfficerAgent()
    # Assuming Radar is desired here too, though not in original chain. Let's add it for fullness.
    from src.agents.radar import RadarAgent
    radar = RadarAgent()

    # Define tasks
    tasks = [
        (analyst, "Analyze the top pick from the previous step.", originator_output),
        (risk_officer, "Simulate impact of this new trade.", originator_output),
        (radar, f"Search for news on the top pick.", originator_output)
    ]
    
    # Run Async Logic Wrapper
    # Since we are in a synchronous Dash callback, we need a helper to run the async loop
    def run_async_in_sync(tasks):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(AgentOrchestrator.run_parallel(tasks))
        loop.close()
        return results

    try:
        results = run_async_in_sync(tasks)
        
        analyst_output = results["Analyst"]
        risk_output = results["RiskOfficer"]
        radar_output = results["Radar"]
        
        log(f"Analyst Output:\n{analyst_output}\n")
        log(f"RiskOfficer Output:\n{risk_output}\n")
        log(f"Radar Output:\n{radar_output}\n")
        
    except Exception as e:
        log(f"ERROR in Parallel Phase: {e}")
        return "\n".join(logs)

    # ----------------------
    
    # ... (Preceding code) ...

    # 3. Architect
    architect = ArchitectAgent()
    log("\n[4/4] @Architect is making the final decision...")
    
    # Get real portfolio context
    from src.utils.data_manager import data_manager
    portfolio_context = data_manager.get_portfolio_context()
    
    final_decision = architect.run(
        "Review the full packet and issue a BUY/PASS decision. Use the Portfolio Snapshot to determine sizing.", 
        context=f"Analyst:\n{analyst_output}\n\nRisk:\n{risk_output}\n\nRadar:\n{radar_output}\n\n{portfolio_context}"
    )
    log(f"Architect Decision:\n{final_decision}\n")
    
    # OUTPUT: Return Structured Dictionary for Rich UI
    return {
        "logs": "\n".join(logs),
        "originator": originator_output,
        "analyst": analyst_output, # JSON String
        "risk": risk_output,       # JSON String
        "radar": radar_output,
        "architect": final_decision # JSON String
    }
