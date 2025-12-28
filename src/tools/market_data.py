import requests
from bs4 import BeautifulSoup
import re

def get_market_data(ticker):
    """
    Fetches financial data primarily from StockAnalysis.com (No API Key, Resilient).
    Falls back to yfinance for Volatility/History if needed.
    """
    print(f"DEBUG: Fetching data for {ticker} from StockAnalysis...")
    
    data = {
        "ticker": ticker.upper(),
        "price": None,
        "revenue_ttm": None,
        "net_income_ttm": None,
        "volatility": 0.35, # Default
        "beta": None,
        "error": None
    }
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Safari/537.36"}
    
    try:
        # 1. Scraping Summary (Price, Beta, Market Cap)
        # URL: https://stockanalysis.com/stocks/pltr/
        url = f"https://stockanalysis.com/stocks/{ticker.lower()}/"
        r = requests.get(url, headers=headers, timeout=6)
        
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # --- price ---
            # Look for big text class (tailored to current site structure)
            # Strategy: Find the first div with 'text-4xl'
            price_candidates = soup.find_all("div", class_=lambda x: x and 'text-4xl' in x)
            if price_candidates:
                # First one is usually the main price
                try:
                    text = price_candidates[0].text.strip().replace(",", "")
                    data["price"] = float(text)
                except:
                    pass
            
            # --- Beta/MarketCap/EPS (Overview Section) ---
            # Search for all table cells or divs
            # StockAnalysis uses a grid. Keys are often "text-gray-500", Values "text-lg font-bold"
            # Reliable way: Search all text nodes.
            text_nodes = soup.find_all(text=True)
            for i, text in enumerate(text_nodes):
                t = text.strip()
                if t == "Market Cap":
                    # Value is likely the next text node or nearby
                    # Just searching next few nodes
                    for j in range(1, 5):
                         if i+j < len(text_nodes):
                             val = text_nodes[i+j].strip()
                             if val and val[0].isdigit(): # Simple check
                                 data["market_cap"] = val # Keep as string (e.g. "450.20B")
                                 break
                
                if t == "EPS (ttm)" or t == "EPS":
                     for j in range(1, 5):
                         if i+j < len(text_nodes):
                             val = text_nodes[i+j].strip()
                             if val and (val[0].isdigit() or val[0] == '-'):
                                 data["eps"] = val
                                 break

        # 2. Scraping Financials (Revenue, Net Income)
        # URL: https://stockanalysis.com/stocks/pltr/financials/
        url_fin = f"https://stockanalysis.com/stocks/{ticker.lower()}/financials/"
        r_fin = requests.get(url_fin, headers=headers, timeout=6)
        
        if r_fin.status_code == 200:
            soup = BeautifulSoup(r_fin.text, 'html.parser')
            table = soup.find("table")
            if table:
                rows = table.find_all("tr")
                for row in rows:
                    cols = row.find_all("td")
                    if not cols: continue
                    label = cols[0].text.strip()
                    
                    # TTM is typically column [1] (Column [0] is Label)
                    # Ex: ['Revenue', '3,896', '2,800'...]
                    # StockAnalysis format: [Label, TTM, LastYear, ...]
                    
                    try:
                        val_str = cols[1].text.strip().replace(",", "")
                        # Values in Millions
                        val_float = float(val_str) * 1_000_000
                        
                        if "Revenue" in label and "Growth" not in label and not data["revenue_ttm"]:
                            data["revenue_ttm"] = val_float
                        

                        if "Net Income" in label and "Growth" not in label and "Common" in label:
                             data["net_income_ttm"] = val_float
                             
                    except:
                        continue
                        
        # 3. Scraping Balance Sheet (Cash, Debt, Shares)
        # URL: https://stockanalysis.com/stocks/pltr/financials/balance-sheet/
        url_bs = f"https://stockanalysis.com/stocks/{ticker.lower()}/financials/balance-sheet/"
        r_bs = requests.get(url_bs, headers=headers, timeout=6)
        
        if r_bs.status_code == 200:
            soup_bs = BeautifulSoup(r_bs.text, 'html.parser')
            table_bs = soup_bs.find("table")
            if table_bs:
                for row in table_bs.find_all("tr"):
                    cols = row.find_all("td")
                    if not cols: continue
                    label = cols[0].text.strip()
                    
                    try:
                        val_str = cols[1].text.strip().replace(",", "")
                        val_float = float(val_str) * 1_000_000
                        
                        if "Cash & Equivalents" in label:
                            data["cash"] = data.get("cash", 0) + val_float
                        if "Short-Term Investments" in label:
                            data["cash"] = data.get("cash", 0) + val_float
                        if "Total Debt" in label:
                            data["debt"] = val_float
                        if "Share Issued" in label or "Ordinary Shares Number" in label:
                            if not data.get("shares"):
                                data["shares"] = val_float
                    except:
                        pass
                        
        # Fallback for Shares (Income Statement usually has Weighted Average Shares)
        # We already parsed Income Statement, but let's check Overview again if needed
        # Or parse Income Statement again for "Shares"
        if not data.get("shares"):
             # Look for "Shares Outstanding" in Overview text
             text_nodes = soup.find_all(text=True)
             for i, text in enumerate(text_nodes):
                if text.strip() == "Shares Out":
                    for j in range(1, 4):
                        if i+j < len(text_nodes):
                             v = text_nodes[i+j].strip()
                             # Format: 2.23B or 500M
                             if v and v[-1] in ['B', 'M', 'K']:
                                 mult = 1e9 if v[-1] == 'B' else 1e6 if v[-1] == 'M' else 1e3
                                 try:
                                     data["shares"] = float(v[:-1]) * mult
                                     break
                                 except: pass

    except Exception as e:
        print(f"DEBUG: StockAnalysis scrape failed: {e}")
        data["error"] = str(e)

    # 3. YFinance Fallback for Volatility (History)
    # We try this gently just for the chart path
    if not data["price"] or not data["volatility"]:
        try:
            import yfinance as yf
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1y")
            if not hist.empty:
                 # If price missing, take it
                 if not data["price"]:
                     data["price"] = hist['Close'].iloc[-1]
                 
                 # Calc Volatility
                 returns = hist['Close'].pct_change().dropna()
                 data["volatility"] = returns.std() * (252**0.5)
        except:
             pass

    # Final Check
    if not data["price"]:
        data["error"] = "Data unavailable from all sources."
        
    # Calculated Metrics (Add P/E if missing)
    if data["price"] and data.get("eps"):
        try:
             eps_val = float(data["eps"])
             if eps_val > 0:
                 data["pe"] = float(data["price"]) / eps_val
        except:
             pass
             
    return data

def get_current_price(ticker):
    d = get_market_data(ticker)
    return d.get("price")
