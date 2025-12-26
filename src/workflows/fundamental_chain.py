from src.agents.analyst import AnalystAgent

def run_fundamental_chain(ticker):
    logs = []
    def log(msg):
        print(msg)
        logs.append(str(msg))

    log(f"--- Starting Fundamental Deep Dive Chain ---")
    log(f"Target Ticker: {ticker}")
    
    analyst = AnalystAgent()
    log("\n@Analyst is conducting due diligence...")
    
    prompt = f"Conduct a comprehensive fundamental analysis on {ticker}. Focus on Quality, Valuation, and Durability."
    analyst_output = analyst.run(prompt)
    
    log(f"Analyst Report:\n{analyst_output}\n")
    
    return "\n".join(logs)
