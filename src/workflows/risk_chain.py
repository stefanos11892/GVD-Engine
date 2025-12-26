from src.agents.risk_officer import RiskOfficerAgent

def run_risk_chain(scenario, target):
    logs = []
    def log(msg):
        print(msg)
        logs.append(str(msg))

    log(f"--- Starting Risk Analysis Chain ---")
    log(f"Scenario: {scenario}")
    log(f"Target: {target}")
    
    risk_officer = RiskOfficerAgent()
    log("\n@RiskOfficer is running stress tests...")
    
    prompt = f"Run a stress test for scenario '{scenario}' on '{target}'. Calculate VaR and potential drawdown."
    risk_output = risk_officer.run(prompt)
    
    log(f"Risk Officer Report:\n{risk_output}\n")
    
    return "\n".join(logs)
