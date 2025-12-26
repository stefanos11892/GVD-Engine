from src.agents.evaluator import EvaluatorAgent
from src.agents.radar import RadarAgent
from src.agents.forecaster import ForecasterAgent
from src.agents.architect import ArchitectAgent

def run_earnings_season_chain(file_path):
    logs = []
    def log(msg):
        print(msg)
        logs.append(str(msg))

    log("--- Starting Workflow B: The 'Earnings Season' Chain ---")
    
    # 1. Evaluator
    evaluator = EvaluatorAgent()
    log(f"\n[1/4] @Evaluator is analyzing {file_path}...")
    # In a real system, we'd read the PDF content here.
    pdf_content = f"Content of {file_path} (Placeholder)" 
    evaluator_output = evaluator.run("Run Mode 1: Deep Dive on this 10-K.", context=pdf_content)
    log(f"Evaluator Output:\n{evaluator_output}\n")
    
    # 2. Radar
    radar = RadarAgent()
    log("\n[2/4] @Radar is checking for news...")
    radar_output = radar.run("Check for recent lawsuits or news for this company.", context=evaluator_output)
    log(f"Radar Output:\n{radar_output}\n")
    
    # 3. Forecaster
    forecaster = ForecasterAgent()
    log("\n[3/4] @Forecaster is updating models...")
    forecaster_output = forecaster.run("Update Base Case model using new numbers.", context=evaluator_output)
    log(f"Forecaster Output:\n{forecaster_output}\n")
    
    # 4. Architect
    architect = ArchitectAgent()
    log("\n[4/4] @Architect is deciding on the thesis...")
    final_decision = architect.run("Decide if the Investment Thesis is broken.", context=f"Evaluator:\n{evaluator_output}\n\nRadar:\n{radar_output}\n\nForecaster:\n{forecaster_output}")
    log(f"Architect Decision:\n{final_decision}\n")
    
    return "\n".join(logs)
