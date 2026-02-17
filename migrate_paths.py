import sqlite3
import os

DB_FILE = "app/database.db"

def fix_paths(s):
    if not s or '|' in s:
        return s
    
    parts = s.split(',')
    new_paths = []
    current_path = ""
    
    for p in parts:
        # p = p.strip() # Don't strip yet, we might need leading space if we re-join
        # actually, splitting by comma usually implies we want to strip the space after comma if it was "a, b"
        # but here the split was inside a filename "Image, 2026". " 2026".
        # If we strip, " 2026" becomes "2026". 
        # If we re-join "Image" + ", " + "2026", we get "Image, 2026".
        
        clean_p = p.strip()
        
        # Check if this part looks like a start of a new path
        # Our paths always start with "app/uploads" or "app\uploads"
        if clean_p.startswith("app/uploads") or clean_p.startswith("app\\uploads"):
            if current_path:
                new_paths.append(current_path)
            current_path = clean_p # Use the clean version for start
        else:
            # Continuation
            if current_path:
                current_path += "," + p # Keep original p to preserve spacing if possible?
                # actually p has the leading space from the split if it was there.
            else:
                # Should not happen if first char is valid, but if bad data
                current_path = clean_p
                
    if current_path:
        new_paths.append(current_path)
        
    return "|".join(new_paths)

def migrate():
    print("Starting migration...")
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        # 1. Design Requests
        rows = c.execute("SELECT id, assets_paths FROM design_requests").fetchall()
        print(f"Checking {len(rows)} design requests...")
        
        for row in rows:
            req_id = row['id']
            curr_assets = row['assets_paths']
            
            if curr_assets and ',' in curr_assets and '|' not in curr_assets:
                new_assets = fix_paths(curr_assets)
                if new_assets != curr_assets:
                    print(f"Fixing {req_id}:")
                    print(f"  Old: {curr_assets}")
                    print(f"  New: {new_assets}")
                    
                    c.execute("UPDATE design_requests SET assets_paths = ? WHERE id = ?", (new_assets, req_id))
        
        # 2. Requirements (checking just in case)
        rows = c.execute("SELECT id, assets_paths FROM requirements").fetchall()
        print(f"Checking {len(rows)} requirements...")
        for row in rows:
            req_id = row['id']
            curr_assets = row['assets_paths']
            
            if curr_assets and ',' in curr_assets and '|' not in curr_assets:
                new_assets = fix_paths(curr_assets)
                if new_assets != curr_assets:
                    print(f"Fixing Req {req_id}: {new_assets}")
                    c.execute("UPDATE requirements SET assets_paths = ? WHERE id = ?", (new_assets, req_id))

        conn.commit()
        print("Migration complete.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    migrate()
