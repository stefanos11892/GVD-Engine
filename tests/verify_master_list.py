import requests
from bs4 import BeautifulSoup

def check_url(url):
    print(f"Checking {url}...")
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            # Look for a big table or list
            table = soup.find("table")
            if table:
                rows = len(table.find_all("tr"))
                print(f"[FOUND] {url} -> Table with {rows} rows.")
                return True
            else: 
                # Maybe a list structure?
                lists = soup.find_all("li")
                print(f"[FOUND] {url} -> Page exists. {len(lists)} list items.")
                return True
        else:
            print(f"[404] {url}")
    except Exception as e:
        print(f"[ERROR] {e}")
    return False

if __name__ == "__main__":
    check_url("https://stockanalysis.com/stocks/") # Likely the master index
    check_url("https://stockanalysis.com/list/all-stocks/")
