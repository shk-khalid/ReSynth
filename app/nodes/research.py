from app.services.search import search
from app.services.scrapper import scrape
from app.services.extractor import extract_facts
from app.state import ResearchState

MAX_SEARCH_RESULTS = 10

def research_node(state: ResearchState):
    all_facts = []
    sources = []
    pages_scraped = 0

    # Single search call using the original user query
    results = search(state["query"], num_results=MAX_SEARCH_RESULTS)

    for result in results:
        sources.append(result)

        text = scrape(result["link"])
        if not text:
            continue

        pages_scraped += 1
        facts = extract_facts(text, result["link"])
        all_facts.extend(facts)

    state["extracted_facts"] = all_facts
    state["sources"] = sources

    # Debug logging
    print(f"--- Research Summary ---")
    print(f"URLs collected: {len(results)}")
    print(f"Pages scraped:  {pages_scraped}")
    print(f"Facts extracted: {len(all_facts)}")

    return state