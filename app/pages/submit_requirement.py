import streamlit as st
import os
import uuid
import datetime
from database import create_requirement
from auth import try_auto_login

st.set_page_config(page_title="Submit Requirement", page_icon="📝", layout="wide", initial_sidebar_state="expanded")

try_auto_login()

from navigation import render_sidebar
render_sidebar()

if not st.session_state.get("logged_in"):
    st.warning("Please log in to access this page.")
    st.stop()

st.title("📝 Submit New Requirement")

with st.form("requirement_form"):
    title = st.text_input("Requirement Title")
    req_type = st.selectbox("Requirement Type", ["Design Change", "Feature Change", "New Requirement", "Bug Fix", "Other"])
    remarks = st.text_area("Remarks / Description")
    
    col1, col2 = st.columns(2)
    with col1:
        current_design = st.file_uploader("Upload Current Design Image", type=['png', 'jpg', 'jpeg'], key="current_design")
    with col2:
        reference_img = st.file_uploader("Upload Reference Image", type=['png', 'jpg', 'jpeg'], key="ref_img")
    
    assets_files = st.file_uploader("Upload Design Assets (Icons, Fonts, SVGs, etc.)", accept_multiple_files=True, key="assets")
    
    submitted = st.form_submit_button("Submit Requirement")
    
    if submitted:
        if not title:
            st.error("Title is required.")
        else:
            req_id = str(uuid.uuid4())[:8]
            
            # Save Current Design
            saved_current_path = None
            if current_design:
                upload_dir = "app/uploads/requirements/current"
                os.makedirs(upload_dir, exist_ok=True)
                file_path = os.path.join(upload_dir, f"{req_id}_current_{current_design.name}")
                with open(file_path, "wb") as f:
                    f.write(current_design.getbuffer())
                saved_current_path = file_path
            
            # Save Reference Image
            saved_ref_path = None
            if reference_img:
                upload_dir = "app/uploads/requirements/refs"
                os.makedirs(upload_dir, exist_ok=True)
                file_path = os.path.join(upload_dir, f"{req_id}_ref_{reference_img.name}")
                with open(file_path, "wb") as f:
                    f.write(reference_img.getbuffer())
                saved_ref_path = file_path
            
            # Save Assets
            saved_asset_paths = []
            if assets_files:
                upload_dir = "app/uploads/requirements/assets"
                os.makedirs(upload_dir, exist_ok=True)
                for asset in assets_files:
                    file_path = os.path.join(upload_dir, f"{req_id}_asset_{asset.name}")
                    with open(file_path, "wb") as f:
                        f.write(asset.getbuffer())
                    saved_asset_paths.append(file_path)

            data = {
                "id": req_id,
                "submitter": st.session_state['user'],
                "title": title,
                "requirement_type": req_type,
                "remarks": remarks,
                "current_design_path": saved_current_path,
                "reference_img_path": saved_ref_path,
                "assets_paths": ",".join(saved_asset_paths)
            }
            
            create_requirement(data)
            st.success(f"Requirement {req_id} submitted successfully!")
            st.info("You can view it in the Requirement Dashboard.")
