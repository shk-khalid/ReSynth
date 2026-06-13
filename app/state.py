from typing import TypedDict, List, Dict

class ResearchState(TypedDict):
    query: str
    research_plan: List[str]
    sources: List[Dict]
    extracted_facts: List[Dict]
    raw_documents: List[str]
    summaries: List[str]
    fact_clusters: List[Dict]
    confidence_scores: Dict
    final_report: str