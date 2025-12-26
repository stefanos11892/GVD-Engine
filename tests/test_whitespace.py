from src.tools.market_data import get_market_data
import json

def test_space():
    ticker = "PLTR "
    print(f"Testing ticker: '{ticker}'")
    data = get_market_data(ticker)
    print("Result:", data.get("error") if data.get("error") else "Success")
    print("Price:", data.get("price"))

if __name__ == "__main__":
    test_space()
