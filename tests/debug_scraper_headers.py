import requests
from bs4 import BeautifulSoup
import sys

def debug_headers(ticker):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Safari/537.36"}
    url_fin = f"https://stockanalysis.com/stocks/{ticker.lower()}/financials/"
    print(f"Fetching {url_fin}...")
    
    r = requests.get(url_fin, headers=headers)
    if r.status_code != 200:
        print(f"Failed: {r.status_code}")
        return

    soup = BeautifulSoup(r.text, 'html.parser')
    table = soup.find("table")
    if table:
        # Print Header Row
        thead = table.find("thead")
        if thead:
            headers = [th.text.strip() for th in thead.find_all("th")]
            print(f"Headers: {headers}")
        else:
            # Maybe it's in the first tr of tbody
            rows = table.find_all("tr")
            if rows:
                headers = [td.text.strip() for td in rows[0].find_all(["th", "td"])]
                print(f"First Row: {headers}")

        # Print First few data rows to map values
        rows = table.find_all("tr")
        for i, row in enumerate(rows[:5]):
            cols = [c.text.strip() for c in row.find_all("td")]
            print(f"Row {i}: {cols}")
    else:
        print("No table found.")

if __name__ == "__main__":
    debug_headers("ADBE")
