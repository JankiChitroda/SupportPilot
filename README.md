# SupportPilot – AI-Powered Ticket Resolution & Triage Agent

SupportPilot is a production-grade, enterprise-ready AI support ticket management and resolution system. It automates ticket ingestion, multi-class categorization, severity prioritization, and knowledge base retrieval using Retrieval-Augmented Generation (RAG), secured via cryptographically signed JSON Web Tokens (JWT).

---

## 🚀 Key Features & Milestones

1. **Secure Authentication (JWT & SQLite):**
   - User registration and login flow backed by an SQLite database.
   - Cryptographically signed JWT authentication stored via secure `httponly` browser cookies.
   - Custom Python decorators (`@token_required`) protecting dashboard and resolution routes.

2. **Milestone 1: AI Ticket Ingestion & Classification:**
   - Real-time natural language processing of incoming support tickets.
   - Built with **Scikit-learn** (`LinearSVC` & `TfidfVectorizer`) to dynamically predict ticket category, urgency severity, and execution priority.
   - Live metrics tracking inference response times and total triaged volume.

3. **Milestone 2: RAG Retrieval & Resolution Generation:**
   - Vector similarity search querying a centralized SQLite knowledge base.
   - Autonomous synthesis engine matching tickets to the highest-confidence Standard Operating Procedure (SOP).
   - Interactive audit trail and one-click execution to resolve tickets.

---

## 🛠️ Tech Stack

* **Backend:** Python, Flask
* **Machine Learning:** Scikit-learn, TF-IDF Vectorization
* **Database:** SQLite (`support_pilot.db`)
* **Security:** PyJWT (JSON Web Tokens)
* **Frontend:** Tailwind CSS, HTML5, JavaScript

---

## 📂 Project Architecture

```text
SupportPilot/
│
├── app.py                  # Main Flask application and route controllers
├── database.py             # SQLite database initialization and data handlers
├── classifier.py           # Scikit-learn ML inference and prediction logic
├── rag_engine.py           # TF-IDF cosine similarity RAG retrieval engine
├── jwt_handler.py          # JWT token generation and route protection decorator
├── requirements.txt        # Project python dependencies
├── support_pilot.db        # Centralized SQLite database
├── models/                 # Pre-trained ML model binaries (.pkl)
│   ├── ticket_classifier.pkl
│   └── tfidf_vectorizer.pkl
└── templates/              # Tailwind-styled frontend HTML pages
    ├── register.html
    ├── login.html
    ├── newTicket.html
    └── resolution.html
