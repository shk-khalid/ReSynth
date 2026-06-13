import re
import math

STOPWORDS = {
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd",
    'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers',
    'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which',
    'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been',
    'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if',
    'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between',
    'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out',
    'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why',
    'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
    'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should',
    "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't",
    'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't",
    'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't",
    'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"
}

def tokenize(text: str):
    """Clean and tokenize string into words, removing stopwords."""
    words = re.findall(r'\b[a-z0-9]+\b', text.lower())
    return [w for w in words if w not in STOPWORDS]

def compute_tfidf_vectors(documents: list[str]) -> list[dict]:
    """Compute TF-IDF vectors normalized to unit length for each document."""
    tokenized_docs = [tokenize(doc) for doc in documents]
    
    # Calculate Document Frequency (DF)
    df = {}
    for doc in tokenized_docs:
        seen = set(doc)
        for word in seen:
            df[word] = df.get(word, 0) + 1
            
    num_docs = len(documents)
    
    # Calculate Inverse Document Frequency (IDF)
    idf = {}
    for word, count in df.items():
        idf[word] = math.log((1 + num_docs) / (1 + count)) + 1
        
    # Compute TF-IDF vectors
    vectors = []
    for doc in tokenized_docs:
        tf = {}
        for word in doc:
            tf[word] = tf.get(word, 0) + 1
            
        vector = {}
        for word, count in tf.items():
            vector[word] = count * idf[word]
            
        # Normalize to unit length (L2 norm)
        squared_sum = sum(val ** 2 for val in vector.values())
        norm = math.sqrt(squared_sum)
        if norm > 0:
            for word in vector:
                vector[word] /= norm
                
        vectors.append(vector)
        
    return vectors

def cosine_similarity(v1: dict, v2: dict) -> float:
    """Calculate the cosine similarity between two unit vectors."""
    dot_product = 0.0
    if len(v1) > len(v2):
        v1, v2 = v2, v1
    for word, val in v1.items():
        if word in v2:
            dot_product += val * v2[word]
    return dot_product

def cluster_facts(facts: list[dict], threshold: float = 0.15) -> list[dict]:
    """
    Groups facts into thematic clusters using TF-IDF cosine similarity.
    Input format: [{'fact': '...', 'source_url': '...'}, ...]
    Output format: [{'theme': '...', 'facts': [...]}, ...]
    """
    if not facts:
        return []

    texts = [f["fact"] for f in facts]
    vectors = compute_tfidf_vectors(texts)
    
    clusters = []  # List of lists of document indices
    
    for i, vec in enumerate(vectors):
        if not vec:
            clusters.append([i])
            continue
            
        best_cluster_idx = -1
        best_similarity = -1.0
        
        for c_idx, cluster in enumerate(clusters):
            total_sim = 0.0
            valid_counts = 0
            for member_idx in cluster:
                if not vectors[member_idx]:
                    continue
                total_sim += cosine_similarity(vec, vectors[member_idx])
                valid_counts += 1
                
            avg_sim = total_sim / valid_counts if valid_counts > 0 else 0.0
            if avg_sim > best_similarity:
                best_similarity = avg_sim
                best_cluster_idx = c_idx
                
        if best_similarity >= threshold:
            clusters[best_cluster_idx].append(i)
        else:
            clusters.append([i])
            
    # Format output clusters with a temporary label
    formatted_clusters = []
    for cluster in clusters:
        cluster_facts = [facts[idx] for idx in cluster]
        
        # Determine a fallback theme using prominent words from the longest fact
        longest_fact = max(cluster_facts, key=lambda f: len(f["fact"]))
        words = tokenize(longest_fact["fact"])
        theme_label = " ".join(words[:4]).title() if words else "General Information"
        
        formatted_clusters.append({
            "theme": theme_label,
            "facts": cluster_facts
        })
        
    return formatted_clusters
