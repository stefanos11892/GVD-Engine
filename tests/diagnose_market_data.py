import sys
import os
sys.path.append(os.getcwd())

from src.tools.market_data import get_market_data

def test_amzn():
    print("Fetching AMZN data...")
    data = get_market_data("AMZN")
    
    print("\n--- RESULTS ---")
    print(f"Price: {data.get('price')}")
    print(f"Market Cap: {data.get('market_cap')}")
    print(f"EPS: {data.get('eps')}")
    print(f"Revenue TTM: {data.get('revenue_ttm')}")
    print(f"Net Income TTM: {data.get('net_income_ttm')}")
    
    # Calculate P/E Manually
    try:
        if data.get('price') and data.get('eps'):
            pe = float(data['price']) / float(data['eps'])
            print(f"Calculated P/E (Price/EPS): {pe:.2f}")
        else:
            print("Cannot calc P/E (missing data)")
    except Exception as e:
        print(f"Calc error: {e}")

if __name__ == "__main__":
    test_amzn()
