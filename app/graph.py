from langgraph.graph import StateGraph
from app.state import ResearchState
from app.nodes.planner import planner_node
from app.nodes.research import research_node
from app.nodes.synthesizer import synthesizer_node

def build_graph():
    builder = StateGraph(ResearchState)

    builder.add_node("planner", planner_node)
    builder.add_node("research", research_node)
    builder.add_node("synthesizer", synthesizer_node)

    builder.set_entry_point("planner")

    builder.add_edge("planner", "research")
    builder.add_edge("research", "synthesizer")
    
    builder.set_finish_point("synthesizer")

    return builder.compile()