from app.llm import generate
from app.state import ResearchState

def synthesizer_node(state: ResearchState):
    if not state["extracted_facts"]:
        state["final_report"] = "Insufficient evidence: no sourced facts found."
        return state

    # Collect unique source URLs for the sources section
    source_urls = list(dict.fromkeys(
        fact["source_url"] for fact in state["extracted_facts"]
    ))
    sources_block = "\n".join(f"- {url}" for url in source_urls)

    fact_clusters = state.get("fact_clusters", [])
    confidence_data = state.get("confidence_scores", {})
    overall_confidence = confidence_data.get("overall_confidence", 0.0)

    # Format clusters and their internal validation metadata for the prompt
    cluster_block = ""
    for cluster in fact_clusters:
        cluster_block += f"### Theme: {cluster['theme']} (Confidence: {cluster['confidence_score']}/1.0)\n"
        for fact in cluster["facts"]:
            cluster_block += f"- {fact['fact']} [Source: {fact['source_url']}]\n"
        if cluster.get("contradictions"):
            cluster_block += "  Contradictions detected in this theme:\n"
            for contradiction in cluster["contradictions"]:
                cluster_block += f"  - WARNING: {contradiction}\n"
        cluster_block += "\n"

    prompt = f"""
    Using ONLY the following clustered facts and validation data, generate a structured research report.

    OVERALL REPORT CONFIDENCE: {overall_confidence} / 1.0

    STRUCTURE:
    1. Executive Summary
    2. Thematic Breakdown (organize findings under the themes provided in the "Clustered Facts" section below. Discuss the facts and mention the individual cluster confidence scores)
    3. Research Quality & Contradictions (summarize overall report confidence, highlight high-confidence sections, and explicitly address any warnings/contradictions flagged below. If none are flagged, state that the sources were highly consistent)
    4. Sources (list ALL source URLs used — copy them exactly from the facts below)

    CITATION RULES (STRICT):
    - Never generate citations such as (Author, Year) or (Organization, Year).
    - Only reference the exact source URLs provided with each fact.
    - Format inline citations as: (Source: <url>)
    - If a source is unknown, omit the citation entirely.
    - Do NOT invent, guess, or fabricate any citation.

    At the END of the report, include this exact section:
    
    Sources:
{sources_block}

    CONTENT RULES:
    - Use ONLY the provided facts. Do not add outside knowledge.
    - Address any contradictions or discrepancies directly in Section 3.

    Clustered Facts & Validation Details:
{cluster_block}
    """

    report = generate(prompt)

    state["final_report"] = report

    return state
