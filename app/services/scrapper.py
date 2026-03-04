import time
import logging
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

# Domains known to block bots, require JS, or return garbage
BLOCKED_DOMAINS = {
    "facebook.com", "instagram.com", "twitter.com", "x.com",
    "linkedin.com", "tiktok.com", "pinterest.com",
    "youtube.com", "reddit.com",
}

MAX_TEXT_LENGTH = 15000
MAX_RETRIES = 3
BASE_DELAY = 1  # seconds


def _is_blocked(url: str) -> bool:
    """Check if the URL belongs to a known-bad domain."""
    from urllib.parse import urlparse
    domain = urlparse(url).netloc.lower()
    return any(blocked in domain for blocked in BLOCKED_DOMAINS)


def scrape(url: str) -> str | None:
    if _is_blocked(url):
        logger.info(f"Skipped blocked domain: {url}")
        return None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            res = requests.get(url, headers=HEADERS, timeout=10)
            res.raise_for_status()

            soup = BeautifulSoup(res.content, "html.parser")

            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.extract()

            text = soup.get_text(separator=" ")
            clean_text = " ".join(text.split())

            return clean_text[:MAX_TEXT_LENGTH]

        except requests.exceptions.HTTPError as e:
            logger.warning(f"HTTP {e.response.status_code} for {url} (attempt {attempt}/{MAX_RETRIES})")
        except requests.exceptions.ConnectionError:
            logger.warning(f"Connection error for {url} (attempt {attempt}/{MAX_RETRIES})")
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout for {url} (attempt {attempt}/{MAX_RETRIES})")
        except Exception as e:
            logger.warning(f"Unexpected error scraping {url}: {e}")
            return None  # Don't retry on unknown errors

        # Exponential backoff before next retry
        if attempt < MAX_RETRIES:
            delay = BASE_DELAY * (2 ** (attempt - 1))
            time.sleep(delay)

    logger.error(f"All {MAX_RETRIES} attempts failed for {url}")
    return None