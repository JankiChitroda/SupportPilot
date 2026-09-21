from flask import Flask, render_template, request, redirect, session, url_for, make_response
from classifier import process_ticket
from database import init_db, save_ticket, save_user, verify_user
import time
import sqlite3
from rag_engine import retrieve_best_kb_article
from jwt_handler import generate_token, token_required

# 1. Initialize Flask app FIRST
app = Flask(__name__)
app.secret_key = "supportpilot_secret_key"

init_db()

# 2. Root Route -> Opens register.html first
@app.route("/")
def home():
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        # Verify credentials against SQLite database users table
        conn = sqlite3.connect("support_pilot.db")
        cursor = conn.cursor()
        cursor.execute("SELECT full_name, email FROM users WHERE email = ? AND password = ?", (email, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            # Generate JWT token upon successful authentication
            token = generate_token(user[0], user[1])
            
            # Save token inside HTTP-only cookie and redirect to ticket dashboard
            resp = make_response(redirect(url_for("ticket_dashboard")))
            resp.set_cookie("auth_token", token, httponly=True)
            return resp
        else:
            error = "Invalid email or password. Please try again."
            
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    # Clear JWT cookie to end session
    resp = make_response(redirect(url_for("login")))
    resp.set_cookie("auth_token", "", expires=0)
    return resp

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("fullName")
        email = request.form.get("email")
        department = request.form.get("department")
        password = request.form.get("password")
        
        success = save_user(full_name, email, department, password)
        if success:
            # Generate JWT token immediately upon registration and log them in
            token = generate_token(full_name, email)
            resp = make_response(redirect(url_for("ticket_dashboard")))
            resp.set_cookie("auth_token", token, httponly=True)
            return resp
        else:
            return "Email already registered or error occurred!", 400
            
    return render_template("register.html")

# 3. Main Milestone 1 Dashboard Route (Protected by JWT)
@app.route("/ticket", methods=["GET", "POST"])
@token_required
def ticket_dashboard():
    prediction_result = None
    inference_time = "0.4s"  # default baseline
    
    if request.method == "POST":
        name = request.form.get("employee_name", "Alex Chen") 
        email = request.form.get("email", "")
        title = request.form.get("title", "")
        description = request.form.get("description", "")
        
        # Measure real-time inference speed
        start_time = time.time()
        ai_output = process_ticket(description, ticket_title=title)
        end_time = time.time()
        
        # Calculate elapsed time in seconds
        elapsed = end_time - start_time
        inference_time = f"{max(elapsed, 0.1):.1f}s"
        
        # Save to SQLite database
        save_ticket(
            name=name,
            email=email,
            title=title,
            description=description,
            category=ai_output["category"],
            severity=ai_output["severity"],
            priority=ai_output["priority"]
        )
        
        prediction_result = ai_output
        prediction_result["employee_name"] = name
        prediction_result["title"] = title
        prediction_result["email"] = email

    # Fetch total triaged tickets count from SQLite database safely
    try:
        conn = sqlite3.connect("support_pilot.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tickets")
        total_triaged = cursor.fetchone()[0]
        conn.close()
    except Exception:
        total_triaged = 0  # Fallback if table doesn't exist yet

    return render_template(
        "newTicket.html", 
        result=prediction_result, 
        inference_time=inference_time,
        total_triaged=total_triaged
    )

#----------- Milestone 2: Resolution & RAG Engine (Protected by JWT) -----------

@app.route("/resolution")
@token_required
def resolution():
    conn = sqlite3.connect("support_pilot.db")
    cursor = conn.cursor()
    
    # Fetch the most recent ticket submitted by the user
    cursor.execute("""
        SELECT id, title, description, category, severity, priority, status, resolution_text 
        FROM tickets ORDER BY id DESC LIMIT 1
    """)
    ticket = cursor.fetchone()
    conn.close()
    
    if ticket:
        ticket_data = {
            "id": f"#T-2026-{ticket[0]:04d}",
            "title": ticket[1],
            "description": ticket[2],
            "category": ticket[3],
            "severity": ticket[4],
            "priority": ticket[5],
            "status": ticket[6],
            "resolution_text": ticket[7]
        }
        # Run RAG retrieval based on category & description
        rag_result = retrieve_best_kb_article(ticket[3], ticket[2])
    else:
        # Fallback dummy ticket if none submitted yet
        ticket_data = {
            "id": "#T-2026-0000",
            "title": "No ticket selected",
            "description": "Please submit a ticket on Milestone 1 first.",
            "category": "General inquiry",
            "severity": "Low",
            "priority": "P4",
            "status": "Pending",
            "resolution_text": None
        }
        rag_result = {
            "title": "Default SOP",
            "steps": "1. Ingest a valid support ticket.",
            "confidence": 0.0
        }

    return render_template("resolution.html", ticket=ticket_data, rag=rag_result)

@app.route("/execute_resolution/<ticket_id>", methods=["POST"])
@token_required
def execute_resolution(ticket_id):
    # Action endpoint when user clicks 'Execute Automated Action'
    resolution_note = request.form.get("resolution_note", "Resolved via Automated RAG Agent.")
    
    # Extract raw numeric ID from #T-2026-XXXX format
    numeric_id = ticket_id.split("-")[-1]
    
    conn = sqlite3.connect("support_pilot.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE tickets SET status = 'Resolved', resolution_text = ? WHERE id = ?
    """, (resolution_note, numeric_id))
    conn.commit()
    conn.close()
    
    return redirect(url_for("resolution"))

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

from agent_workflow import run_multi_agent_pipeline

@app.route("/milestone3_dashboard", methods=["GET", "POST"])
@token_required
def milestone3_dashboard():
    pipeline_result = None
    
    if request.method == "POST":
        title = request.form.get("title", "Automated Task")
        description = request.form.get("description", "")
        category = request.form.get("category", "Technical")
        
        # Execute the multi-agent pipeline
        pipeline_result = run_multi_agent_pipeline(title, description, category)
        
    return render_template("multiAgent.html", result=pipeline_result)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)