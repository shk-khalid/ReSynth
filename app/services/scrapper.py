import requests
from bs4 import BeautifulSoup

def scrape(url: str):
    try: 
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.content, "html.parser")

        for script in soup(["script", "style"]):
            script.extract()

        text = soup.get_text(seperator=" ")
        clean_text = " ".join(text.split())

        return clean_text[:15000]
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None