from app.services.search import search
from app.services.scrapper import scrape
from app.services.extractor import extract_facts
from app.state import ResearchState

MAX_SEARCH_RESULTS = 10

def research_node(state: ResearchState):
    all_facts = []
    sources = []

    # Single search call using the original user query
    results = search(state["query"], num_results=MAX_SEARCH_RESULTS)

    for result in results:
        sources.append(result)

        text = scrape(result["link"])
        if not text:
            continue

        facts = extract_facts(text, result["link"])
        all_facts.extend(facts)

    state["extracted_facts"] = all_facts
    state["sources"] = sources

    return state