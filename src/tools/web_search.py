try:
    from duckduckgo_search import DDGS
except ImportError:
    try:
        from duckduckgo_search import ddg as DDGS # Old version fallback
    except ImportError:
        DDGS = None

def search_web(query):
    """
    Searches the web using DuckDuckGo and returns a list of results.
    """
    if DDGS:
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=5))
                formatted_results = ""
                for r in results:
                    formatted_results += f"Title: {r['title']}\nLink: {r['href']}\nSnippet: {r['body']}\n\n"
                return formatted_results
        except Exception as e:
            return f"Error searching web: {str(e)}"
    return "DuckDuckGo Search not available."
