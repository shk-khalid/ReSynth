from app.llm import generate
from app.state import ResearchState

def synthesizer_node(state: ResearchState):
    if not state["extracted_facts"]:
        state["final_report"] = "Insufficient evidence: no sourced facts found."
        return state

    fact_block = ""
    for fact in state["extracted_facts"]:
        fact_block += f"- {fact['fact']} (Source: {fact['source_url']})\n"

    # Use themes from planner to guide report structure
    themes = state.get("research_plan", [])
    theme_block = "\n".join(f"  - {t}" for t in themes) if themes else "  - General overview"

    prompt = f"""
    Using ONLY the following extracted facts, generate a structured research report.

    STRUCTURE:
    1. Executive Summary
    2. Thematic Breakdown (organize findings under these themes):
{theme_block}
    3. Key Findings & Data Points

    CITATION RULES (STRICT):
    - Never generate citations such as (Author, Year) or (Organization, Year).
    - Only reference the exact source URLs provided with each fact.
    - Format citations as: (Source: <url>)
    - If a source is unknown, omit the citation entirely.
    - Do NOT invent, guess, or fabricate any citation.

    CONTENT RULES:
    - Use ONLY the provided facts. Do not add outside knowledge.
    - If a theme has no supporting facts, state that explicitly.

    Facts: 
    {fact_block}
    """

    report = generate(prompt)

    state["final_report"] = report

    return state
