import streamlit as st
import sqlite3
import os

st.title("Debug Page (Internal)")

st.write(f"CWD: {os.getcwd()}")

REQ_ID = "DES-E53A31"
DB_FILE = "app/database.db"

try:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT assets_paths FROM design_requests WHERE id=?", (REQ_ID,)).fetchone()
    
    if row:
        raw = row['assets_paths']
        st.code(f"DB Raw: '{raw}'")
        
        if '|' in raw:
            parts = raw.split('|')
            st.write(f"Split by |: {parts}")
        else:
             st.write("No | found.")
             parts = raw.split(',') 
             st.write(f"Split by , (legacy): {parts}")
             
        for p in parts:
            p = p.strip()
            exists = os.path.exists(p)
            st.write(f"Checking '{p}': `{exists}`")
            if not exists:
                st.write(f"  Abs Path: `{os.path.abspath(p)}`")
            
    else:
        st.error(f"Req {REQ_ID} not found.")

except Exception as e:
    st.error(f"Error: {e}")
finally:
    if 'conn' in locals(): conn.close()
