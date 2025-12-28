import sys
import os
import logging
from unittest.mock import patch, MagicMock

sys.path.append(os.getcwd())

# Setup console logging to catch 'log_debug'
logging.basicConfig(level=logging.DEBUG)

def mock_get_market_data(ticker):
    print(f"[MOCK] Returning data for {ticker}")
    if ticker == "GOOGL":
        return {
            "ticker": "GOOGL",
            "price": 313.51,
            "pe": 30.92,
            "revenue_ttm": 300000000000,
            "net_income_ttm": 80000000000,
            "eps": 10.14
        }
    elif ticker == "META":
        return {
            "ticker": "META",
            "price": 663.29,
            "pe": 28.5,
            "revenue_ttm": 150000000000,
            "net_income_ttm": 50000000000,
            "eps": 22.63
        }
    return {}

def mock_search_web(query):
    return "Mock Search Results: Great company, dominant market leader."

def audit_logic_offline():
    print("--- AUDIT: OFFLINE LOGIC CHECK ---")
    
    # Patch dependencies
    with patch('src.agents.analyst.get_market_data', side_effect=mock_get_market_data), \
         patch('src.agents.analyst.search_web', side_effect=mock_search_web):
         
        from src.agents.analyst import AnalystAgent
        agent = AnalystAgent()
        
        # Override log_debug to capture "Black Box" data
        def capture_log(msg):
            print(f"[Captured Log] {msg}")
        agent.log_debug = capture_log
        
        print("\n--- TEST CASE 1: GOOGL (High PE, High Quality) ---")
        # Logic: PE 30.92 / 1.5 = 20.6% Growth.
        # Anchor should be ~$350+.
        agent.run("Analyze GOOGL")
        
        print("\n--- TEST CASE 2: META (High Price, High PE) ---")
        # Logic: PE 28.5. Growth ~19%.
        # Anchor should verify vs $663 Price.
        agent.run("Analyze META")

if __name__ == "__main__":
    audit_logic_offline()
