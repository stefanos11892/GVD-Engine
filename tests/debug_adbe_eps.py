import sys
import os
from src.tools.market_data import get_market_data

# Fix Path
sys.path.append(os.getcwd())

def debug_adbe():
    print("Fetching ADBE Data...")
    data = get_market_data("ADBE")
    print(data)
    
    price = data.get("price")
    eps = data.get("eps")
    
    if price and eps:
        pe = price / float(eps)
        print(f"Calculated PE: {pe}")
    else:
        print("Missing Price or EPS")

if __name__ == "__main__":
    debug_adbe()
