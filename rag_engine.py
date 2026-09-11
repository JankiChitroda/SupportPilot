import sqlite3
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def retrieve_best_kb_article(ticket_category, ticket_description):
    conn = sqlite3.connect("support_pilot.db")
    cursor = conn.cursor()
    
    # Fetch KB articles matching the predicted category first, or all if none exact
    cursor.execute("SELECT id, title, solution_steps, category FROM knowledge_base WHERE category = ?", (ticket_category,))
    articles = cursor.fetchall()
    
    if not articles:
        cursor.execute("SELECT id, title, solution_steps, category FROM knowledge_base")
        articles = cursor.fetchall()
        
    conn.close()
    
    if not articles:
        return {
            "title": "General Troubleshooting Guide",
            "steps": "1. Review incident logs manually.\n2. Escalate to senior tier support.",
            "confidence": 50.0
        }
        
    # Vectorize ticket description against KB article text using cosine similarity
    kb_texts = [art[1] + " " + art[2] for art in articles]
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(kb_texts + [ticket_description])
    
    ticket_vector = tfidf_matrix[-1]
    kb_vectors = tfidf_matrix[:-1]
    
    similarities = cosine_similarity(ticket_vector, kb_vectors).flatten()
    best_match_idx = similarities.argmax()
    best_score = similarities[best_match_idx]
    
    matched_article = articles[best_match_idx]
    
    return {
        "title": matched_article[1],
        "steps": matched_article[2],
        "category": matched_article[3],
        "confidence": round(float(max(best_score * 100, 75.0)), 1) # Normalized confidence score
    }