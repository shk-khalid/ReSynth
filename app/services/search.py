import os
import requests
from dotenv import load_dotenv

load_dotenv()

SERPER_API_KEY = os.getenv("SERPER_API_KEY")

def search(query: str, num_results: int = 10):
    
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