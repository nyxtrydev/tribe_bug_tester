import sqlite3
import os
import datetime
import bcrypt

DB_FILE = "app/database.db"

def get_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()

    # Users Table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL,
                    is_approved BOOLEAN DEFAULT 0
                )''')

    # Migration for is_approved
    try:
        c.execute("ALTER TABLE users ADD COLUMN is_approved BOOLEAN DEFAULT 0")
        print("Migrated users table with is_approved column.")
    except sqlite3.OperationalError:
        pass # Column likely exists

    # Issues Table
    c.execute('''CREATE TABLE IF NOT EXISTS issues (
                    id TEXT PRIMARY KEY,
                    submitter TEXT NOT NULL,
                    account_type TEXT,
                    issue_type TEXT,
                    screen_name TEXT,
                    title TEXT,
                    description TEXT,
                    steps_to_reproduce TEXT,
                    expected_result TEXT,
                    actual_result TEXT,
                    severity TEXT,
                    status TEXT DEFAULT 'Open',
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP,
                    file_paths TEXT,
                    test_username TEXT,
                    test_password TEXT,
                    test_email TEXT
                )''')

    # Migration for new columns (safe-ish for dev)
    try:
        c.execute("ALTER TABLE issues ADD COLUMN test_username TEXT")
        c.execute("ALTER TABLE issues ADD COLUMN test_password TEXT")
        c.execute("ALTER TABLE issues ADD COLUMN test_email TEXT")
        print("Migrated issues table with test credentials columns.")
    except sqlite3.OperationalError:
        pass # Columns likely exist

    # Comments Table
    c.execute('''CREATE TABLE IF NOT EXISTS comments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    issue_id TEXT,
                    username TEXT,
                    comment TEXT,
                    created_at TIMESTAMP,
                    FOREIGN KEY(issue_id) REFERENCES issues(id)
                )''')

    # Auto Test Results Table
    c.execute('''CREATE TABLE IF NOT EXISTS auto_test_results (
                    issue_id TEXT PRIMARY KEY,
                    duplicate_score REAL,
                    missing_info TEXT,
                    suggested_severity TEXT,
                    qa_score INTEGER,
                    FOREIGN KEY(issue_id) REFERENCES issues(id)
                )''')


    # Create Super Admin (abhiraman)
    # Create Super Admin (abhiraman) - Updated Password
    c.execute("SELECT * FROM users WHERE username = 'abhiraman'")
    row = c.fetchone()
    if not row:
        password = "Tribe#123#@".encode('utf-8')
        hashed = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')
        c.execute("INSERT INTO users (username, password_hash, role, is_approved) VALUES (?, ?, ?, ?)", 
                  ("abhiraman", hashed, "Admin", 1))
        print("Super Admin created: abhiraman")
    else:
        # Update existing super admin to be approved and have new password if needed
        # We'll just ensure they are approved. Password update might require manual intervention 
        # or we force update it here. Let's force update for this request.
        password = "Tribe#123#@".encode('utf-8')
        hashed = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')
        c.execute("UPDATE users SET is_approved = 1, password_hash = ? WHERE username = 'abhiraman'", (hashed,))
        print("Super Admin updated.")

    conn.commit()

    # Design Requests Table
    c.execute('''CREATE TABLE IF NOT EXISTS design_requests (
                    id TEXT PRIMARY KEY,
                    submitter TEXT NOT NULL,
                    screen_name TEXT,
                    design_references TEXT,
                    notes TEXT,
                    priority TEXT,
                    status TEXT DEFAULT 'Open',
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP,
                    file_paths TEXT,
                    reference_img_paths TEXT
                )''')
    
    # Migration for reference_img_paths
    try:
        c.execute("ALTER TABLE design_requests ADD COLUMN reference_img_paths TEXT")
        print("Migrated design_requests table with reference_img_paths column.")
    except sqlite3.OperationalError:
        pass 

    conn.commit()
    conn.close()


# --- Design Requests ---
def create_design_request(data):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''INSERT INTO design_requests (id, submitter, screen_name, design_references, notes, 
                                              priority, status, created_at, updated_at, file_paths, reference_img_paths)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (data['id'], data['submitter'], data['screen_name'], data['design_references'], 
               data['notes'], data['priority'], 'Open', datetime.datetime.now(), datetime.datetime.now(), 
               data.get('file_paths'), data.get('reference_img_paths')))
    conn.commit()
    conn.close()

def get_all_design_requests():
    conn = get_connection()
    reqs = conn.execute("SELECT * FROM design_requests ORDER BY created_at DESC").fetchall()
    conn.close()
    return reqs

def get_design_request_by_id(req_id):
    conn = get_connection()
    req = conn.execute("SELECT * FROM design_requests WHERE id = ?", (req_id,)).fetchone()
    conn.close()
    return req

def update_design_request_status(req_id, new_status):
    conn = get_connection()
    conn.execute("UPDATE design_requests SET status = ?, updated_at = ? WHERE id = ?", 
                 (new_status, datetime.datetime.now(), req_id))
    conn.commit()
    conn.close()

def update_design_request_details(req_id, notes, priority, file_paths, reference_img_paths):
    conn = get_connection()
    conn.execute('''UPDATE design_requests 
                    SET notes = ?, priority = ?, file_paths = ?, reference_img_paths = ?, updated_at = ? 
                    WHERE id = ?''', 
                 (notes, priority, file_paths, reference_img_paths, datetime.datetime.now(), req_id))
    conn.commit()
    conn.close()

def delete_design_request(req_id):
    conn = get_connection()
    conn.execute("DELETE FROM design_requests WHERE id = ?", (req_id,))
    conn.commit()
    conn.close()

# --- Issues ---
def create_issue(issue_data):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''INSERT INTO issues (id, submitter, account_type, issue_type, screen_name, title, description, 
                                     steps_to_reproduce, expected_result, actual_result, severity, status, 
                                     created_at, updated_at, file_paths, test_username, test_password, test_email)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (issue_data['id'], issue_data['submitter'], issue_data['account_type'], issue_data['issue_type'],
               issue_data['screen_name'], issue_data['title'], issue_data['description'], 
               issue_data.get('steps_to_reproduce'), issue_data.get('expected_result'), issue_data.get('actual_result'),
               issue_data['severity'], 'Open', datetime.datetime.now(), datetime.datetime.now(), 
               issue_data.get('file_paths'),
               issue_data.get('test_username'), issue_data.get('test_password'), issue_data.get('test_email')))
    conn.commit()
    conn.close()

def get_all_issues():
    conn = get_connection()
    issues = conn.execute("SELECT * FROM issues ORDER BY created_at DESC").fetchall()
    conn.close()
    return issues

def get_issue_by_id(issue_id):
    conn = get_connection()
    issue = conn.execute("SELECT * FROM issues WHERE id = ?", (issue_id,)).fetchone()
    conn.close()
    return issue

def update_status(issue_id, new_status):
    conn = get_connection()
    conn.execute("UPDATE issues SET status = ?, updated_at = ? WHERE id = ?", 
                 (new_status, datetime.datetime.now(), issue_id))
    conn.commit()
    conn.close()

def delete_issue(issue_id):
    conn = get_connection()
    conn.execute("DELETE FROM issues WHERE id = ?", (issue_id,))
    conn.execute("DELETE FROM comments WHERE issue_id = ?", (issue_id,))
    conn.execute("DELETE FROM auto_test_results WHERE issue_id = ?", (issue_id,))
    conn.commit()
    conn.close()

def update_issue_details(issue_id, steps, expected, actual):
    conn = get_connection()
    conn.execute('''UPDATE issues 
                    SET steps_to_reproduce = ?, expected_result = ?, actual_result = ?, updated_at = ? 
                    WHERE id = ?''', 
                 (steps, expected, actual, datetime.datetime.now(), issue_id))
    conn.commit()
    conn.close()

# --- Comments ---
def add_comment(issue_id, username, comment):
    conn = get_connection()
    conn.execute("INSERT INTO comments (issue_id, username, comment, created_at) VALUES (?, ?, ?, ?)",
                 (issue_id, username, comment, datetime.datetime.now()))
    conn.commit()
    conn.close()

def get_comments(issue_id):
    conn = get_connection()
    comments = conn.execute("SELECT * FROM comments WHERE issue_id = ? ORDER BY created_at ASC", (issue_id,)).fetchall()
    conn.close()
    return comments

# --- Auto Test Results ---
def save_auto_test_results(issue_id, results):
    conn = get_connection()
    conn.execute("INSERT OR REPLACE INTO auto_test_results (issue_id, duplicate_score, missing_info, suggested_severity, qa_score) VALUES (?, ?, ?, ?, ?)",
                 (issue_id, results['duplicate_score'], results['missing_info'], results['suggested_severity'], results['qa_score']))
    conn.commit()
    conn.close()

def get_auto_test_results(issue_id):
    conn = get_connection()
    result = conn.execute("SELECT * FROM auto_test_results WHERE issue_id = ?", (issue_id,)).fetchone()
    conn.close()
    return result

# --- Users ---
def create_user(username, password_hash, role, is_approved=False):
    conn = get_connection()
    try:
        conn.execute("INSERT INTO users (username, password_hash, role, is_approved) VALUES (?, ?, ?, ?)", 
                     (username, password_hash, role, is_approved))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user(username):
    conn = get_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return user

def get_pending_users():
    conn = get_connection()
    users = conn.execute("SELECT * FROM users WHERE is_approved = 0").fetchall()
    conn.close()
    return users

def approve_user(username):
    conn = get_connection()
    conn.execute("UPDATE users SET is_approved = 1 WHERE username = ?", (username,))
    conn.commit()
    conn.close()

# --- Helpers ---
def get_recent_test_credentials():
    conn = get_connection()
    # Get distinct sets of credentials used recently
    query = '''
        SELECT test_username, test_password, test_email, MAX(created_at) as last_used 
        FROM issues 
        WHERE test_username IS NOT NULL AND test_username != ''
        GROUP BY test_username, test_password, test_email 
        ORDER BY last_used DESC 
        LIMIT 5
    '''
    creds = conn.execute(query).fetchall()
    conn.close()
    return creds
