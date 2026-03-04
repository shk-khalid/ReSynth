import json
from app.llm import generate_json
from app.state import ResearchState

MAX_SUB_QUERIES = 4

def planner_node(state: ResearchState):
    prompt = f"""
    Break the following research query into 3-4 focused sub-questions for web search.

    Respond ONLY with valid JSON in this exact format:
    {{ "sub_queries": ["question 1", "question 2", "question 3"] }}

    Query: {state['query']}
    """

    raw = generate_json(prompt)

    try:
        parsed = json.loads(raw)
        sub_queries = parsed.get("sub_queries", [])

        if not isinstance(sub_queries, list) or len(sub_queries) == 0:
            raise ValueError("Invalid or empty sub_queries")

        # Cap to MAX_SUB_QUERIES
        sub_queries = [q.strip() for q in sub_queries[:MAX_SUB_QUERIES] if isinstance(q, str) and q.strip()]

        if not sub_queries:
            raise ValueError("No valid sub-queries after filtering")

    except (json.JSONDecodeError, ValueError, KeyError) as e:
        print(f"Planner JSON parse failed ({e}), falling back to original query.")
        sub_queries = [state["query"]]

    state["research_plan"] = sub_queries

    return state