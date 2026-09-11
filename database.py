import sqlite3

DB_NAME = "support_pilot.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. Tickets Table (Tracks lifecycle, resolutions, and user metadata)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            title TEXT,
            description TEXT,
            category TEXT,
            severity TEXT,
            priority TEXT,
            status TEXT DEFAULT 'Open',
            resolution_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2. Users Table for Registration & Login
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT,
            email TEXT UNIQUE,
            department TEXT,
            password TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 3. Knowledge Base (KB) Table for RAG Retrieval
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_base (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            title TEXT,
            solution_steps TEXT
        )
    """)
    
    # Seed sample SOPs if empty
    cursor.execute("SELECT COUNT(*) FROM knowledge_base")
    if cursor.fetchone()[0] == 0:
        sample_sops = [
            ("Technical / Infrastructure", "Cloud Server Outage Recovery", 
             "1. Isolate the affected US-East database cluster.\n2. Flush connection pool and restart service workers via CLI.\n3. Verify health check endpoints and notify DevOps on-call webhook."),
            ("Technical / Network", "VPN Connectivity Restoration", 
             "1. Check corporate gateway routing tables.\n2. Reset user session authentication tokens in LDAP/Active Directory.\n3. Instruct user to clear local DNS cache (`ipconfig /flushdns`) and reconnect."),
            ("Billing inquiry", "Billing Charge & Refund Protocol", 
             "1. Verify transaction ID in Stripe payment gateway ledger.\n2. Review subscription tier parameters for prorated adjustments.\n3. Issue automated credit note or clarification response to client."),
            ("General inquiry", "Software License Provisioning", 
             "1. Confirm departmental budget approval status.\n2. Generate corporate software license key via procurement portal.\n3. Send automated onboarding guide and license file to requester.")
        ]
        cursor.executemany("INSERT INTO knowledge_base (category, title, solution_steps) VALUES (?, ?, ?)", sample_sops)
        
    conn.commit()
    conn.close()

def save_ticket(name, email, title, description, category, severity, priority):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO tickets (name, email, title, description, category, severity, priority, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'Open')
    ''', (name, email, title, description, category, severity, priority))
    conn.commit()
    conn.close()

def save_user(full_name, email, department, password):
    """Saves a new registered user to the database. Returns True if successful, False if email already exists."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO users (full_name, email, department, password)
            VALUES (?, ?, ?, ?)
        ''', (full_name, email, department, password))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    finally:
        conn.close()
    return success

def verify_user(full_name, password):
    """Verifies user credentials against the users table. Returns user record if valid, else None."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM users WHERE full_name = ? AND password = ?
    ''', (full_name, password))
    user = cursor.fetchone()
    conn.close()
    return user

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully with users, tickets, and knowledge base tables!")