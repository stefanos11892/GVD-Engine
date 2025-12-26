import sys
import os
import json
import time
from src.tools.market_data import get_market_data
from src.tools.web_search import search_web
from src.agents.analyst import AnalystAgent
from src.logic.valuation import ValuationEngine

# Fix Path
sys.path.append(os.getcwd())

def audit_ticker(ticker):
    print(f"\n{'='*20} AUDIT REPORT: {ticker} {'='*20}")
    
    # 1. Fetch System Data
    print("[1] Fetching System Data...")
    market_data = get_market_data(ticker)
    sys_price = market_data.get('price')
    sys_rev = market_data.get('revenue_ttm')
    eps_val = market_data.get('eps')
    try:
        eps = float(eps_val) if eps_val else 1.0 # Avoid ZeroDivision
    except:
        eps = 1.0
        
    sys_pe = sys_price / eps
    
    print(f"    - System Price: ${sys_price}")
    print(f"    - System Revenue (TTM): ${sys_rev/1e9:.2f}B")
    print(f"    - System P/E: {sys_pe:.2f}x")
    
    # 2. Ground Truth Check
    print("\n[2] Checking Ground Truth (Web Search)...")
    truth_query = f"{ticker} stock price revenue ttm pe ratio"
    truth = search_web(truth_query)
    # We visually verify the print output
    safe_truth = truth.encode('ascii', 'ignore').decode('ascii')
    print(f"    - Web Snippet: {safe_truth[:300]}...") 
    
    # 3. Agent Execution (with Independent Thinking)
    print("\n[3] Generating AI Investment Memo...")
    agent = AnalystAgent()
    
    # Feed the data like the dashboard does
    context = json.dumps(market_data, indent=2)
    prompt = f"Analyze {ticker}. STRICTLY use this dashboard data for valuation metrics: {context}"
    
    start_time = time.time()
    response = agent.run(prompt)
    duration = time.time() - start_time
    
    print(f"\n[4] AI Verdict (Generated in {duration:.1f}s):")
    
    # Parse JSON simple
    try:
        import re
        if "```json" in response:
             json_str = response.split("```json")[1].split("```")[0]
        elif "{" in response:
             start = response.find("{")
             end = response.rfind("}")
             json_str = response[start:end+1]
        
        data = json.loads(json_str)
        print(f"    - Rating: {data.get('rating')}")
        print(f"    - Fair Value: {data.get('fair_value_range')}")
        print(f"    - Rationales: {data.get('score_rationale')}")
        print(f"    - Detailed Analysis: {data.get('detailed_analysis')[:150]}...")
        
    except Exception as e:
        print(f"    - ERROR Parsing JSON: {e}")
        print(response)

def main():
    audit_ticker("ADBE")
    audit_ticker("AMD")

if __name__ == "__main__":
    main()
