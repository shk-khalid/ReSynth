import re
from urllib.parse import urlparse
from app.state import ResearchState

MAX_FACTS = 30

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

        # Track domain for diversity
        source = fact.get("source_url", fact.get("source", ""))
        domain = urlparse(source).netloc if source else "unknown"
        domain_counts[domain] = domain_counts.get(domain, 0) + 1

        seen.add(normalized)
        unique_facts.append(fact)

    # Sort to prefer facts from less-represented domains (source diversity)
    unique_facts.sort(
        key=lambda f: domain_counts.get(
            urlparse(f.get("source_url", f.get("source", ""))).netloc, 0
        )
    )

    # Cap at MAX_FACTS
    state["extracted_facts"] = unique_facts[:MAX_FACTS]

    return state
