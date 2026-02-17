import streamlit as st
import os
import uuid
import datetime
from database import create_design_request
from auth import try_auto_login

st.set_page_config(page_title="Submit Design Request", page_icon="🖌️", layout="wide", initial_sidebar_state="expanded")

try_auto_login()

from navigation import render_sidebar
render_sidebar()

if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("Please log in to access this page.")
    st.stop()

st.title("🎨 Submit Design Update")

with st.form("design_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        screen_name = st.text_input("Screen/Page Name", placeholder="e.g., Login Page, Dashboard")
        priority = st.selectbox("Priority", ["High", "Medium", "Low"])
    
    with col2:
        design_refs = st.text_area("Design References (Links/Figma)", height=100)
        
    notes = st.text_area("Notes / Description of Changes", height=150)
    
    uploaded_files = st.file_uploader("Upload Design Mocks/Screenshots", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'], key="mocks")
    reference_files = st.file_uploader("Upload Reference Images (Optional)", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'], key="refs")
    
    submitted = st.form_submit_button("Submit Request")
    
    if submitted:
        if not screen_name:
            st.error("Screen Name is required.")
        else:
            req_id = f"DES-{uuid.uuid4().hex[:6].upper()}"
            
            # Save Mocks
            saved_file_paths = []
            if uploaded_files:
                upload_dir = "app/uploads/designs" 
                for uploaded_file in uploaded_files:
                    file_path = os.path.join(upload_dir, f"{req_id}_mock_{uploaded_file.name}")
                    # Ensure directory exists
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    saved_file_paths.append(file_path)

            # Save References
            saved_ref_paths = []
            if reference_files:
                ref_dir = "app/uploads/references" 
                for uploaded_file in reference_files:
                    file_path = os.path.join(ref_dir, f"{req_id}_ref_{uploaded_file.name}")
                    # Ensure directory exists
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    saved_ref_paths.append(file_path)
            
            # Create Design Request Data
            design_data = {
                "id": req_id,
                "submitter": st.session_state["user"],
                "screen_name": screen_name,
                "design_references": design_refs,
                "notes": notes,
                "priority": priority,
                "file_paths": ",".join(saved_file_paths),
                "reference_img_paths": ",".join(saved_ref_paths)
            }
            
            create_design_request(design_data)
            
            st.success(f"Design Request {req_id} submitted successfully!")
