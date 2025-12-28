from src.agents.originator import OriginatorAgent
try:
    from src.tools.screener import fetch_stock_screener
except ImportError:
    import sys
    import os
    sys.path.append(os.getcwd())
    from src.tools.screener import fetch_stock_screener

def verify_sector_expansion():
    queries = [
        "Find me the best mining company",
        "Looking for undervalued pharma stocks",
        "Best bank to buy now",
        "Invest in clean energy",
        "Next big AI stock"
    ]
    
    agent = OriginatorAgent()
    
    print("--- VERIFYING ORIGINATOR LOGIC ---")
    for q in queries:
        # We want to see what category it picks. 
        # I'll modify the agent temporarily or just infer from output?
        # Actually, let's just inspect the logic block in Originator.run via print if possible.
        # But since I can't easily modify the class for print without edit, I'll rely on the fact that fetch_stock_screener prints DEBUG.
        
        print(f"\nQUERY: '{q}'")
        # Run agent
        # We mock fetch_stock_screener to just print category? 
        # No, let's run it for real to verify the NETWORK link too.
        
        response = agent.run(q)
        # Check output contains expected Tickers or references
        print(f"RESPONSE SNIPPET: {response[:100]}...")

if __name__ == "__main__":
    verify_sector_expansion()
