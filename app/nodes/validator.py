import json
import logging
from app.llm import generate_json
from app.services.clustering import cluster_facts
from app.state import ResearchState

logger = logging.getLogger(__name__)

def validator_node(state: ResearchState):
    facts = state.get("extracted_facts", [])
    if not facts:
        state["fact_clusters"] = []
        state["confidence_scores"] = {
            "overall_confidence": 0.0,
            "cluster_scores": {},
            "contradictions": []
        }
        return state

    # Step 1: Run TF-IDF clustering
    raw_clusters = cluster_facts(facts, threshold=0.15)
    
    # Step 2: Format clusters for LLM inspection
    clusters_input = []
    for idx, cluster in enumerate(raw_clusters):
        facts_list = []
        for f in cluster["facts"]:
            facts_list.append(f"{f['fact']} [Source: {f['source_url']}]")
        clusters_input.append({
            "index": idx,
            "facts": facts_list
        })
        
    prompt = f"""
    Analyze the following thematic clusters of extracted facts for consistency and credibility.
    For each cluster:
    1. Formulate a clean, concise thematic title.
    2. Identify any contradictions, particularly numeric contradictions (e.g. conflicting percentages, currencies, counts, or temporal contradictions) across the facts in that cluster.
    3. Compute a confidence score (from 0.0 to 1.0):
       - Boost the score (up to 1.0) if multiple independent sources agree on the same claim/numbers.
       - Penalize the score heavily (down to 0.1 - 0.4) if there are contradictions.
       - Set to around 0.5 - 0.6 if it is a single uncorroborated claim with no other source to agree or disagree.
    
    Respond ONLY with a valid JSON object in this exact format:
    {{
      "clusters": [
        {{
          "index": 0,
          "theme": "Clean descriptive theme title",
          "confidence_score": 0.85,
          "contradictions": [
            "Source A says X while Source B says Y"
          ]
        }}
      ]
    }}

    Clusters:
    {json.dumps(clusters_input, indent=2)}
    """
    
    # Call local LLM to validate the clusters
    raw_response = generate_json(prompt)
    
    validated_clusters = []
    all_contradictions = []
    
    try:
        parsed = json.loads(raw_response)
        llm_clusters = {c["index"]: c for c in parsed.get("clusters", []) if "index" in c}
        
        for idx, cluster in enumerate(raw_clusters):
            llm_data = llm_clusters.get(idx, {})
            theme = llm_data.get("theme", cluster["theme"])
            confidence = llm_data.get("confidence_score", 0.5)
            contradictions = llm_data.get("contradictions", [])
            
            # Ensure types are correct
            try:
                confidence = float(confidence)
            except (ValueError, TypeError):
                confidence = 0.5
                
            if not isinstance(contradictions, list):
                contradictions = []
                
            validated_clusters.append({
                "theme": theme,
                "facts": cluster["facts"],
                "confidence_score": confidence,
                "contradictions": contradictions
            })
            all_contradictions.extend(contradictions)
            
    except Exception as e:
        logger.error(f"Validator LLM JSON parsing failed: {e}. Falling back to default scoring.")
        print(f"Validator LLM JSON parsing failed: {e}. Falling back to default scoring.")
        # Fallback scoring:
        for cluster in raw_clusters:
            num_facts = len(cluster["facts"])
            confidence = 0.8 if num_facts > 1 else 0.5
            validated_clusters.append({
                "theme": cluster["theme"],
                "facts": cluster["facts"],
                "confidence_score": confidence,
                "contradictions": []
            })

    # Calculate overall average confidence score
    if validated_clusters:
        overall_conf = sum(c["confidence_score"] for c in validated_clusters) / len(validated_clusters)
    else:
        overall_conf = 0.0
        
    state["fact_clusters"] = validated_clusters
    state["confidence_scores"] = {
        "overall_confidence": round(overall_conf, 2),
        "cluster_scores": {c["theme"]: c["confidence_score"] for c in validated_clusters},
        "contradictions": all_contradictions
    }
    
    print(f"--- Validation Summary ---")
    print(f"Overall Confidence: {state['confidence_scores']['overall_confidence']}")
    print(f"Total Clusters: {len(validated_clusters)}")
    print(f"Total Contradictions: {len(all_contradictions)}")
    
    return state
