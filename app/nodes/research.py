from app.services.search import search
from app.services.scrapper import scrape
from app.services.extractor import extract_facts
from app.state import ResearchState

def research_node(state: ResearchState):
    all_facts = []
    sources = []

    for sub_query in state["research_plan"]:
        results = search(sub_query)

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
    
    