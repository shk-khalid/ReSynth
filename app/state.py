from typing import TypedDict, List, Dict

class ResearchState(TypedDict):
    query: str
    research_plan: List[str]
    sources: List[Dict]
    extracted_facts: List[Dict]
    summaries: List[str]
    final_reports: str