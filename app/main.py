from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import ollama
from app.graph import build_graph

class ResearchRequest(BaseModel):
    query: str

app = FastAPI()

@app.exception_handler(ConnectionError)
def connection_error_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "error": "Ollama service is not running",
            "detail": "Failed to connect to the local Ollama service. Please ensure Ollama is running.",
            "suggestion": "Run 'ollama serve' in your terminal or start the Ollama desktop application."
        }
    )

@app.exception_handler(ollama.ResponseError)
def ollama_response_error_handler(request, exc):
    if exc.status_code == 404:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": "Required Ollama model not found",
                "detail": str(exc),
                "suggestion": "Please pull the required model by running 'ollama pull mistral' in your terminal."
            }
        )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Ollama service returned an error",
            "detail": str(exc)
        }
    )

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