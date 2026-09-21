import time
from rag_engine import retrieve_best_kb_article

def run_multi_agent_pipeline(ticket_title, ticket_description, category):
    # Generate a unique dynamic ticket ID
    ticket_id = f"#IT-2026-{int(time.time()) % 10000:04d}"

    # Agent 1: Sentiment & Urgency Evaluation
    urgency_score = "High Priority" if any(word in ticket_description.lower() for word in ["urgent", "down", "failing", "timeout", "error"]) else "Normal Priority"

    # Agent 2: Knowledge Base RAG Search
    kb_match = retrieve_best_kb_article(category, ticket_description)
    kb_title = kb_match.get('title', 'General SOP') if isinstance(kb_match, dict) else 'General SOP'
    kb_steps = kb_match.get('steps', 'Please wait for support agent review.') if isinstance(kb_match, dict) else 'Please wait for support agent review.'

    # Agent 3: Draft Automated Response
    draft_response = f"Troubleshooting workflow initialized. Recommended actions: {kb_steps}"

    # Summary text for Jira card integration
    summary_text = f"{ticket_title} - Automated Escalation & Routing via RAG Diagnostic Engine"

    agent_trace = [
        {"agent": "Triage & Sentiment Agent", "status": "Completed", "detail": f"Assessed urgency as {urgency_score}."},
        {"agent": "RAG Retrieval Agent", "status": "Completed", "detail": f"Matched KB article: '{kb_title}'."},
        {"agent": "Drafting Agent", "status": "Completed", "detail": "Generated automated customer response template and resolution steps."}
    ]

    return {
        "ticket_id": ticket_id,
        "title": ticket_title,
        "summary": summary_text,
        "urgency": urgency_score,
        "kb_match": kb_match,
        "draft": draft_response,
        "trace": agent_trace
    }