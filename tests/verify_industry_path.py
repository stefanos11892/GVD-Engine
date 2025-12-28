import requests

def check_industry(slug):
    url = f"https://stockanalysis.com/industry/{slug}/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=5)
        print(f"Checking {url} -> Status {r.status_code}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_industry("other-industrial-metals-mining")
    check_industry("oil-gas-drilling")
    check_industry("biotechnology")
