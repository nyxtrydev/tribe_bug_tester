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
                    role TEXT NOT NULL
                )''')

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
                    file_paths TEXT
                )''')

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
    c.execute("SELECT * FROM users WHERE username = 'abhiraman'")
    if not c.fetchone():
        password = "123456@".encode('utf-8')
        hashed = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')
        c.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", 
                  ("abhiraman", hashed, "Admin"))
        print("Super Admin created: abhiraman")

    conn.commit()
    conn.close()

# --- Issues ---
def create_issue(issue_data):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''INSERT INTO issues (id, submitter, account_type, issue_type, screen_name, title, description, 
                                     steps_to_reproduce, expected_result, actual_result, severity, status, 
                                     created_at, updated_at, file_paths)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (issue_data['id'], issue_data['submitter'], issue_data['account_type'], issue_data['issue_type'],
               issue_data['screen_name'], issue_data['title'], issue_data['description'], 
               issue_data.get('steps_to_reproduce'), issue_data.get('expected_result'), issue_data.get('actual_result'),
               issue_data['severity'], 'Open', datetime.datetime.now(), datetime.datetime.now(), 
               issue_data.get('file_paths')))
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
def create_user(username, password_hash, role):
    conn = get_connection()
    try:
        conn.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", 
                     (username, password_hash, role))
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
