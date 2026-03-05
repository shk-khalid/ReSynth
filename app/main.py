from fastapi import FastAPI
from pydantic import BaseModel
from app.graph import build_graph

class ResearchRequest(BaseModel):
    query: str

app = FastAPI()

graph = build_graph()

BASE_PATH = "/api/v1"


@app.get("/")
def root():
    return {
        "service": "ReSynth - A Grounded Research Engine",
        "status": "running"
    }


@app.get(f"{BASE_PATH}/health")
def health():
    return {
        "status": "ok"
    }


@app.post(f"{BASE_PATH}/research")
def research(request: ResearchRequest):
    query = request.query
    initial_state = {
        "query": query,
        "research_plan": [],
        "sources": [],
        "raw_documents": [],
        "extracted_facts": [],
        "summaries": [],
        "final_report": ""
    }

    result = graph.invoke(initial_state)

    return {
        "query": query,
        "facts_extracted": len(result["extracted_facts"]),
        "sources_used": len(result["sources"]),
        "report": result["final_report"]
    }