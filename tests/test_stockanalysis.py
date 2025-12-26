import requests
from bs4 import BeautifulSoup

def test_stockanalysis(ticker):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Safari/537.36"
    }
    
    # 1. Price
    url_summary = f"https://stockanalysis.com/stocks/{ticker.lower()}/"
    print(f"Fetching {url_summary}...")
    try:
        r = requests.get(url_summary, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Price is usually in a div with text-4xl or similar classes, or by checking the first price-like text
        # StockAnalysis structure: <div class="text-4xl font-bold inline-block">194.17</div>
        # Let's try finding the main price.
        price_div = soup.find("div", class_="text-4xl font-bold inline-block")
        if price_div:
            print(f"Price Found: {price_div.text.strip()}")
        else:
            print("Price div not found. Dumping candidates:")
            # Fallback search
            for div in soup.find_all("div", class_="text-4xl"):
                print(f"Cand: {div.text}")
                
    except Exception as e:
        print(f"Summary failed: {e}")

    # 2. Financials
    url_fin = f"https://stockanalysis.com/stocks/{ticker.lower()}/financials/"
    print(f"Fetching {url_fin}...")
    try:
        r = requests.get(url_fin, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Revenue is in the table. 
        # Look for "Total Revenue" row.
        # Table is usually standard HTML table.
        table = soup.find("table")
        if table:
            # Find row with "Revenue"
            rows = table.find_all("tr")
            for row in rows:
                cols = row.find_all("td")
                if not cols: continue
                # First col has label
                label = cols[0].text.strip()
                if "Revenue" in label and "Growth" not in label:
                    # Last column is usually TTM or most recent year?
                    # Actually StockAnalysis columns are Year Descending (TTM, 2024, 2023...)
                    # Second column (index 1) is usually TTM.
                    print(f"Revenue Row Found: {[c.text.strip() for c in cols]}")
                if "Net Income" in label:
                    print(f"Net Income Row Found: {[c.text.strip() for c in cols]}")

    except Exception as e:
        print(f"Financials failed: {e}")

if __name__ == "__main__":
    test_stockanalysis("PLTR")
