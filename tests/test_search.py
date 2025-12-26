try:
    from duckduckgo_search import DDGS
    print("Import successful.")
except ImportError as e:
    print(f"Import failed: {e}")
    exit()

def test_search():
    query = "PLTR stock price TTM revenue"
    print(f"Searching for: {query}")
    try:
        with DDGS() as ddgs:
            # Try basic search
            results = list(ddgs.text(query, max_results=5))
            print(f"Found {len(results)} results:")
            for r in results:
                # Safe print
                try:
                    print(f"Title: {r['title']}")
                    print(f"Link: {r['href']}")
                    print(f"Body: {r['body']}".encode('utf-8', errors='ignore').decode('utf-8')) # Decode back for terminal
                    print("-" * 20)
                except:
                   pass
    except Exception as e:
        print(f"Search failed: {e}")

if __name__ == "__main__":
    test_search()
