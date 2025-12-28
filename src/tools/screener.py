import requests
from bs4 import BeautifulSoup

def fetch_stock_screener(category="undervalued"):
    """
    Scrapes a stock list from StockAnalysis.com to find investment candidates.
    Args:
        category (str): 'undervalued', 'growth', 'technology', 'profitable', etc.
                         Maps to https://stockanalysis.com/list/{category}-stocks/
    Returns:
        list[dict]: A list of stocks with Symbol, Name, P/E, MarketCap.
    """
    
    # Map common terms to valid StockAnalysis slugs (Exact URLs)
    mapping = {
        "undervalued": "mega-cap-stocks", # Fallback: Screener will list big caps, Agent will pick value
        "growth": "nasdaq-100-stocks",    # Fallback: Tech heavy
        "tech": "nasdaq-100-stocks",
        "technology": "nasdaq-100-stocks",
        "compounders": "biggest-companies",
        "biggest": "biggest-companies",
        "dividend": "top-rated-dividend-stocks",
        "quality": "biggest-companies",
        # --- Sector Expansion (Verified Lists) ---
        "mining": "rare-earth",               # Best proxy for strategic miners
        "pharma": "pharmaceutical-stocks",
        "healthcare": "pharmaceutical-stocks",
        "energy": "clean-energy",             # Best proxy for modern energy
        "banks": "bank-stocks",
        "finance": "bank-stocks",
        "ai": "ai-stocks",
        "semis": "semiconductor-stocks",
        "semiconductors": "semiconductor-stocks"
    }
    
    slug = mapping.get(category.lower(), category.lower().replace(" ", "-"))
    
    # Only append suffix if it's NOT a mapped exact match
    if category.lower() not in mapping:
         if not slug.endswith("-stocks") and not slug.endswith("-companies"):
            slug += "-stocks"
        
    url = f"https://stockanalysis.com/list/{slug}/"
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Safari/537.36"}
    print(f"DEBUG: Screener fetching {url}...")
    
    results = []
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200:
            return [{"error": f"Failed to fetch list: {r.status_code}"}]
            
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Determine Table Structure
        # Usually it's the main <table>
        table = soup.find("table")
        if not table:
            return [{"error": "No table found on page."}]
            
        # Parse Headers
        # Symbol is usually Col 1 (No), Col 2 (Symbol), Col 3 (Name)
        # Check output of first row to allow dynamic mapping?
        # For simplicity, we assume standard structure or iterate to find Symbol
        
        headers = [th.text.strip().lower() for th in table.find_all("th")]
        # Example: ['no.', 'symbol', 'company name', 'market cap', 'pe ratio', 'price', 'change', 'volume']
        
        try:
            sym_idx = headers.index('symbol')
            name_idx = headers.index('company name')
        except:
            # Fallback indices
            sym_idx = 1
            name_idx = 2
            
        rows = table.find_all("tr")[1:] # Skip header
        
        for row in rows[:20]: # Limit to top 20 to avoid overwhelming context
            cols = row.find_all("td")
            if not cols: continue
            
            ticker = cols[sym_idx].text.strip()
            name = cols[name_idx].text.strip()
            
            # Extract other useful metrics if available
            metrics = []
            for i, col in enumerate(cols):
                if i not in [sym_idx, name_idx]:
                    metrics.append(col.text.strip())
            
            results.append({
                "ticker": ticker,
                "name": name,
                "details": ", ".join(metrics[:5]) # Grab first few data points (Price, PE, etc)
            })
            
    except Exception as e:
        return [{"error": str(e)}]
        
    return results

if __name__ == "__main__":
    # Internal Test
    data = fetch_stock_screener("undervalued")
    print("Found:", len(data))
    print(data[:3])
