import re
from urllib.parse import urlparse
from app.state import ResearchState

MAX_FACTS = 40
MAX_PER_DOMAIN = 3

def _normalize(text: str) -> str:
    """Lowercase, strip whitespace, remove punctuation."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    text = " ".join(text.split())
    return text

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

    # Cap at MAX_FACTS
    state["extracted_facts"] = unique_facts[:MAX_FACTS]

    return state
