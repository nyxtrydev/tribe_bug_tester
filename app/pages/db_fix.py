import streamlit as st
import sqlite3
import os

st.title("🔧 Database Fixer")

DB_FILE = "app/database.db"

if st.button("Run Fix (Add assets_paths column)"):
    if not os.path.exists(DB_FILE):
        st.error(f"Database file not found at {DB_FILE}")
    else:
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            
            st.write("Checking 'design_requests' table...")
            range_info = c.execute("PRAGMA table_info(design_requests)").fetchall()
            columns = [col[1] for col in range_info]
            st.write(f"Current columns: {columns}")
            
            if 'assets_paths' not in columns:
                st.write("Adding 'assets_paths' column...")
                c.execute("ALTER TABLE design_requests ADD COLUMN assets_paths TEXT")
                conn.commit()
                st.success("SUCCESS: 'assets_paths' column added.")
            else:
                st.info("INFO: 'assets_paths' column already exists.")
                
            conn.close()
            st.write("Current columns after check:")
            # Re-check
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            range_info = c.execute("PRAGMA table_info(design_requests)").fetchall()
            columns = [col[1] for col in range_info]
            st.write(f"{columns}")
            conn.close()
            
        except Exception as e:
            st.error(f"Error: {e}")
