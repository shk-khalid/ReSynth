from langgraph.graph import StateGraph
from app.state import ResearchState
from app.nodes.planner import planner_node
from app.nodes.research import research_node
from app.nodes.deduplicator import deduplicator_node
from app.nodes.validator import validator_node
from app.nodes.synthesizer import synthesizer_node

def build_graph():
    builder = StateGraph(ResearchState)

    builder.add_node("planner", planner_node)
    builder.add_node("research", research_node)
    builder.add_node("deduplicator", deduplicator_node)
    builder.add_node("validator", validator_node)
    builder.add_node("synthesizer", synthesizer_node)

    builder.set_entry_point("planner")

    builder.add_edge("planner", "research")
    builder.add_edge("research", "deduplicator")
    builder.add_edge("deduplicator", "validator")
    builder.add_edge("validator", "synthesizer")
    
    builder.set_finish_point("synthesizer")

    return builder.compile()