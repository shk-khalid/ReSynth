from app.llm import generate
from app.state import ResearchState

def synthesizer_node(state: ResearchState):
    fact_block = ""

    for fact in state["extracted_facts"]:
        fact_block += f"- {fact['fact']} (Source: {fact['source_url']})\n"

    prompt = f"""
    Using ONLY the following extracted facts, generate:

    1. Executive Summary
    2. Thematic Breakdown 
    3. Preserve all citations

    Facts: 
    {fact_block}
    """

    report = generate(prompt)

    state["final_report"] = report

    return state
