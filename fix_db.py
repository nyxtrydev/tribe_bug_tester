import sqlite3
import os
import sys

# Use absolute path to ensure we hit the right file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "app", "database.db")
LOG_FILE = os.path.join(BASE_DIR, "fix_db.log")

def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")
    print(msg)

def fix_db():
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
        
    log(f"Starting fix_db.py...")
    log(f"Looking for database at: {DB_FILE}")
    
    if not os.path.exists(DB_FILE):
        log(f"ERROR: Database file not found at {DB_FILE}")
        return

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    log("Checking 'design_requests' table...")
    try:
        # Check existing columns
        range_info = c.execute("PRAGMA table_info(design_requests)").fetchall()
        columns = [col[1] for col in range_info]
        log(f"Current columns in 'design_requests': {columns}")
        
        if 'assets_paths' not in columns:
            log("Adding 'assets_paths' column...")
            c.execute("ALTER TABLE design_requests ADD COLUMN assets_paths TEXT")
            conn.commit()
            log("SUCCESS: 'assets_paths' column added.")
        else:
            log("INFO: 'assets_paths' column already exists.")
            
    except Exception as e:
        log(f"EXCEPTION: {e}")
    finally:
        conn.close()
        log("Finished fix_db.py")

if __name__ == "__main__":
    fix_db()
