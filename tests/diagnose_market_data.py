from src.tools.market_data import get_market_data
import json

def diagnose():
    print("--- 1. Testing get_market_data('PLTR') ---")
    data = get_market_data("PLTR")
    print("\n--- Raw Output ---")
    print(json.dumps(data, indent=2, default=str))
    
    print("\n--- 2. Checking Keys ---")
    if data.get("error"):
        print(f"CRITICAL: Tool returned error: {data['error']}")
    else:
        print(f"Price: {data.get('price')} (Type: {type(data.get('price'))})")
        print(f"Revenue: {data.get('revenue_ttm')}")
        print(f"Metrics: {data.get('metrics')}") # This key doesn't exist in tool, agent constructs it.
        
if __name__ == "__main__":
    diagnose()
