import sqlite3
import os
import sys

LOG_FILE = "verify_log.txt"

def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")
    print(msg)

try:
    log("Starting verification...")
    REQ_ID = "DES-E53A31" 
    DB_FILE = "app/database.db"
    
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT assets_paths FROM design_requests WHERE id=?", (REQ_ID,)).fetchone()
    
    if row:
        raw = row['assets_paths']
        log(f"DB Raw: '{raw}'")
        
        if '|' in raw:
            parts = raw.split('|')
            log(f"Split by |: {parts}")
        else:
             log("No | found.")
             parts = raw.split(',') 
             log(f"Split by , (legacy): {parts}")
             
        for p in parts:
            p = p.strip()
            exists = os.path.exists(p)
            log(f"Checking '{p}': {exists}")
            if not exists:
                log(f"  Abs Path: {os.path.abspath(p)}")
            
    else:
        log(f"Req {REQ_ID} not found.")

except Exception as e:
    log(f"Error: {e}")
finally:
    if 'conn' in locals(): conn.close()
