import yfinance as yf

def test_yf():
    ticker = "ADBE"
    print(f"Fetching {ticker} via YF...")
    stock = yf.Ticker(ticker)
    info = stock.info
    
    print(f"Trailing PE: {info.get('trailingPE')}")
    print(f"Forward PE: {info.get('forwardPE')}")
    print(f"Trailing EPS: {info.get('trailingEps')}")
    print(f"Forward EPS: {info.get('forwardEps')}")
    print(f"Current Price: {info.get('currentPrice')}")

if __name__ == "__main__":
    test_yf()
