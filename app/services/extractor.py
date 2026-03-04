import re 

# Universal fact signals — no topic-specific keywords
FACT_PATTERNS = [
    r"\d+%",             # percentages
    r"\$[\d,.]+",        # currency (USD)
    r"€[\d,.]+",         # currency (EUR)
    r"£[\d,.]+",         # currency (GBP)
    r"\b\d{4}\b",        # years
    r"\b\d+[\d,.]*\s*(million|billion|trillion|thousand)\b",  # large numbers
]

GROWTH_WORDS = re.compile(
    r"\b(grew|growth|increase|decrease|decline|rose|fell|dropped|surged|"
    r"expanded|shrank|gained|lost|doubled|tripled|raised|reduced)\b",
    re.IGNORECASE
)

def extract_facts(text: str, source_url: str):
    sentences = re.split(r"(?<=[.!?])\s+", text)
    facts = []

    for sentence in sentences:
        has_signal = any(re.search(p, sentence) for p in FACT_PATTERNS)
        has_growth = bool(GROWTH_WORDS.search(sentence))

        if has_signal or has_growth:
            facts.append({
                "fact": sentence.strip(),
                "source_url": source_url
            })

    return facts