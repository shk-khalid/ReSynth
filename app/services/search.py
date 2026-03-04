import os
from tavily import TavilyClient
from ddgs import DDGS
from dotenv import load_dotenv

load_dotenv()

SERPER_API_KEY = os.getenv("SERPER_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

tavily = TavilyClient(api_key=TAVILY_API_KEY)

def tavily_search(query: str, num_results: int = 10):
    try:
        response = tavily.search(
            query=query,
            search_depth="advanced",
            max_results=num_results,
        )

        results = []

        for r in response["results"]:
            results.append({
                "title": r["title"],
                "link": r["url"],
                "snippet": r["content"]
            })

        return results
    except Exception as e:
        print(f"Error in tavily_search: {e}")
        return []
    

def duckduckgo_search(query: str, num_results: int= 5):

    results = []

    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=num_results):
                results.append({
                    "title": r["title"],
                    "link": r["href"],
                "snippet": r["body"]
            })

    except Exception as e:
        print(f"Error in duckduckgo_search: {e}")
        return []

    return results

def serper_search(query: str, num_results: int = 5):
    
    url = "https://google.serper.dev/search"

    payload = {
        "q": query, 
        "num": num_results
    }

    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    results = response.json()

    return  [
        {
            "title": r["title"],
            "link": r["link"],
            "snippet": r["snippet"]
        }
        for r in results.get("organic", [])
    ]

def search(query: str, num_results: int = 5):
    """
    Primary search: Tavily
    Fallback search: DuckDuckGo
    """
    # results = duckduckgo_search(query, num_results)

    results = tavily_search(query, num_results)
    if not results: 
        print("Tavily failed. Falling back to DuckDuckGo.")
        results = duckduckgo_search(query, num_results)

    return results
   