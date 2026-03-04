import json
from app.llm import generate_json
from app.state import ResearchState

MAX_THEMES = 4

def planner_node(state: ResearchState):
    prompt = f"""
    Analyze the following research query and identify 3-4 key themes or subtopics 
    that a comprehensive report should cover.

    These are NOT search queries — they are thematic categories for organizing research findings.

    Respond ONLY with valid JSON in this exact format:
    {{ "themes": ["theme 1", "theme 2", "theme 3"] }}

    Query: {state['query']}
    """

    raw = generate_json(prompt)

    try:
        parsed = json.loads(raw)
        themes = parsed.get("themes", [])

        if not isinstance(themes, list) or len(themes) == 0:
            raise ValueError("Invalid or empty themes")

        themes = [t.strip() for t in themes[:MAX_THEMES] if isinstance(t, str) and t.strip()]

        if not themes:
            raise ValueError("No valid themes after filtering")

    except (json.JSONDecodeError, ValueError, KeyError) as e:
        print(f"Planner JSON parse failed ({e}), falling back to original query as theme.")
        themes = [state["query"]]

    state["research_plan"] = themes

    return state