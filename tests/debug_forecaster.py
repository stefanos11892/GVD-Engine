from src.agents.forecaster import ForecasterAgent

def debug_forecaster():
    agent = ForecasterAgent()
    print("--- Running Forecaster for PLTR ---")
    response = agent.run("Forecast for PLTR")
    print("\n--- Raw Response ---")
    print(response)

if __name__ == "__main__":
    debug_forecaster()
