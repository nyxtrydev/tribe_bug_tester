import sqlite3
import os

try:
    conn = sqlite3.connect('app/database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    row = cursor.execute("SELECT * FROM design_requests ORDER BY created_at DESC LIMIT 1").fetchone()
    
    if row:
        print(f"Design ID: {row['id']}")
        assets_paths = row['assets_paths']
        print(f"Raw assets_paths: '{assets_paths}'")
        
        if assets_paths:
            paths = [p.strip() for p in assets_paths.split(',') if p.strip()]
            print(f"Parsed paths: {paths}")
            
            print(f"CWD: {os.getcwd()}")
            
            for p in paths:
                exists = os.path.exists(p)
                print(f"Path: '{p}' | Exists: {exists}")
                if not exists:
                    # Try with absolute path just in case
                    abs_path = os.path.abspath(p)
                    print(f"  Abs Path: '{abs_path}' | Exists: {os.path.exists(abs_path)}")
        else:
            print("No assets_paths found.")
    else:
        print("No design requests found.")

except Exception as e:
    print(f"Error: {e}")
finally:
    if 'conn' in locals():
        conn.close()
