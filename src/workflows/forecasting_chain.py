from src.agents.forecaster import ForecasterAgent

def run_forecasting_chain(ticker):
    logs = []
    def log(msg):
        print(msg)
        logs.append(str(msg))

    log(f"--- Starting Financial Forecasting Chain ---")
    log(f"Target Ticker: {ticker}")
    
    forecaster = ForecasterAgent()
    log("\n@Forecaster is building models...")
    
    prompt = f"Generate a 5-year financial forecast for {ticker}. Include Bull, Bear, and Base cases."
    forecast_output = forecaster.run(prompt)
    
    log(f"Forecaster Report:\n{forecast_output}\n")
    
    return forecast_output
