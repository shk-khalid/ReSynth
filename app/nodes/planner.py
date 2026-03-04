from app.llm import generate
from app.state import ResearchState

def planner_node(state: ResearchState):
    prompt = f"""
    Break the following research query into 3-5 structured sub-questions: 

    {state['query']}
    """

    plan = generate(prompt)

    state["research_plan"] = [p.strip() for p in plan.split("\n") if p.strip()]

    return state

    