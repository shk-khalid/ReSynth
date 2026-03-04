from app.llm import generate
from app.state import ResearchState

def synthesizer_node(state: ResearchState):
    if not state["extracted_facts"]:
        state["final_report"] = "Insufficient evidence: no sourced facts found."
        return state

    fact_block = ""

    for fact in state["extracted_facts"]:
        fact_block += f"- {fact['fact']} (Source: {fact['source_url']})\n"

    prompt = f"""
    Using ONLY the following extracted facts, generate:

    1. Executive Summary
    2. Thematic Breakdown 
    3. Preserve all citations

    CITATION RULES (STRICT):
    - Never generate citations such as (Author, Year) or (Organization, Year).
    - Only reference the exact source URLs provided with each fact.
    - Format citations as: (Source: <url>)
    - If a source is unknown, omit the citation entirely.
    - Do NOT invent, guess, or fabricate any citation.

    Facts: 
    {fact_block}
    """

    report = generate(prompt)

    state["final_report"] = report

    return state
