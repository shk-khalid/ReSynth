import re
import logging
from urllib.parse import urlparse
from app.state import ResearchState

logger = logging.getLogger(__name__)

MAX_FACTS = 40
MAX_PER_DOMAIN = 2

# Patterns that indicate strong factual content
IMPORTANCE_PATTERNS = [
    r"\d+%",                 # percentages
    r"[\$€£][\d,.]+",        # currency
    r"\b\d{4}\b",            # years
    r"\b\d+[\d,.]*\s*(million|billion|trillion)\b",  # large numbers
]

def _normalize(text: str) -> str:
    """Lowercase, strip whitespace, remove punctuation."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    text = " ".join(text.split())
    return text

def _importance_score(fact_text: str) -> int:
    """Higher score = more factual signals present."""
    return sum(1 for p in IMPORTANCE_PATTERNS if re.search(p, fact_text))

def deduplicator_node(state: ResearchState):
    seen = set()
    unique_facts = []
    domain_counts = {}

    for fact in state["extracted_facts"]:
        normalized = _normalize(fact["fact"])

        if normalized in seen or not normalized:
            continue

        # Domain diversity: cap facts per domain
        source = fact.get("source_url", "")
        domain = urlparse(source).netloc if source else "unknown"

        if domain_counts.get(domain, 0) >= MAX_PER_DOMAIN:
            continue

        seen.add(normalized)
        domain_counts[domain] = domain_counts.get(domain, 0) + 1
        unique_facts.append(fact)

    # Sort by importance: facts with more numeric/data signals first
    unique_facts.sort(key=lambda f: _importance_score(f["fact"]), reverse=True)

    # Cap at MAX_FACTS
    state["extracted_facts"] = unique_facts[:MAX_FACTS]

    logger.info(f"Deduplication: {len(seen)} unique → {len(state['extracted_facts'])} after cap (domains: {len(domain_counts)})")
    print(f"Facts after dedupe: {len(state['extracted_facts'])} (from {len(domain_counts)} domains)")

    return state
