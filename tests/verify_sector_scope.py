import requests
from bs4 import BeautifulSoup

def check_list(slug):
    url = f"https://stockanalysis.com/list/{slug}/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            # Count rows in the main table
            table = soup.find("table")
            if table:
                rows = len(table.find_all("tr")) - 1 # Minus header
                print(f"[VALID] /list/{slug}/ -> {rows} Stocks found.")
                return rows
            else:
                print(f"[VALID] /list/{slug}/ -> Page exists but no table found.")
        else:
            print(f"[INVALID] /list/{slug}/ -> Status {r.status_code}")
    except Exception as e:
        print(f"[ERROR] {slug}: {e}")
    return 0

def scope_audit():
    print("--- AUDITING POTENTIAL UNIVERSE ---")
    
    # Final Candidate Slugs
    test_slugs = [
        "rare-earth",               # Confirmed by Sitemap
        "pharmaceutical-stocks",    # Confirmed
        "clean-energy",             # Confirmed by Sitemap
        "bank-stocks",              # Confirmed by Sitemap
        "ai-stocks",                # Confirmed by Sitemap
        "semiconductor-stocks",     # Confirmed valid earlier
        "other-industrial-metals-mining", # Strong Search Candidate
        "oil-gas-drilling",         # Guess
        "oil-gas-production"        # Guess
    ]
    
    total_new_coverage = 0
    for slug in test_slugs:
        count = check_list(slug)
        total_new_coverage += count
        
    print(f"\nSample of {len(test_slugs)} lists adds {total_new_coverage} potential stocks.")
    print("Estimated Total Universe (100+ Lists): 3000-5000+ Stocks.")

if __name__ == "__main__":
    scope_audit()
