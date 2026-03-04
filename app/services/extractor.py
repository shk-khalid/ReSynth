import re 

def extract_facts(text: str, source_url: str):
    sentences = re.split(r"(?<=[.!?])\s+", text)
    facts = []

    for sentence in sentences:
        if (
            re.search(r"\d+%", sentence) 
            or re.search(r"\$\d+", sentence)
            or re.search(r"\d{4}", sentence)
        ):
            facts.append({
                "fact": sentence.strip(),
                "source_url": source_url
            })
    return facts