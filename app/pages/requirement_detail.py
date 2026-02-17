import streamlit as st
import os
import datetime
from database import get_requirement_by_id, update_requirement_status, update_requirement_details, get_requirement_comments, add_requirement_comment
from auth import try_auto_login

st.set_page_config(page_title="Requirement Details", page_icon="📄", layout="wide", initial_sidebar_state="expanded")

try_auto_login()

from navigation import render_sidebar
render_sidebar()

if not st.session_state.get("logged_in"):
    st.warning("Please log in to access this page.")
    st.stop()

# Get ID from Session State
req_id = st.session_state.get('selected_req_id')
if not req_id:
    st.error("No requirement selected.")
    st.page_link("pages/requirement_dashboard.py", label="Back to Dashboard", icon="🔙")
    st.stop()

req = get_requirement_by_id(req_id)
if not req:
    st.error("Requirement not found.")
    st.stop()

st.title(f"Requirement Details: {req['title']} ({req['id']})")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Description / Remarks")
    st.write(req['remarks'])
    
    st.divider()
    
    # Images Section
    st.subheader("Images")
    col_img1, col_img2 = st.columns(2)
    with col_img1:
        st.write("**Current Design:**")
        if req['current_design_path'] and os.path.exists(req['current_design_path']):
            st.image(req['current_design_path'], use_container_width=True)
        else:
            st.info("No current design image uploaded.")
            
    with col_img2:
        st.write("**Reference Image:**")
        if req['reference_img_path'] and os.path.exists(req['reference_img_path']):
            st.image(req['reference_img_path'], use_container_width=True)
        else:
            st.info("No reference image uploaded.")

    st.divider()
    
    # Assets Section
    if req['assets_paths']:
        st.subheader("📂 Design Assets")
        asset_paths = req['assets_paths'].split(',')
        for path in asset_paths:
            if os.path.exists(path):
                file_name = os.path.basename(path)
                st.write(f"📄 [{file_name}]({path})") # Simple link for now, maybe download button later
                # If image, show it
                if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.svg')):
                     st.image(path, caption=file_name, width=200)
    
    st.divider()
    
    # Chat-like Remarks
    st.subheader("💬 Chat Remarks")
    comments = get_requirement_comments(req_id)
    
    # Display existing comments
    for msg in comments:
        with st.chat_message(msg['username']):
            st.write(f"**{msg['username']}** ({msg['created_at'].strftime('%Y-%m-%d %H:%M')})")
            st.write(msg['comment'])

    # Add new comment
    comment_input = st.chat_input("Add a remark...")
    if comment_input:
        add_requirement_comment(req_id, st.session_state['user'], comment_input)
        st.rerun()

with col2:
    st.subheader("Metadata")
    st.write(f"**Status:** {req['status']}")
    st.write(f"**Type:** {req['requirement_type']}")
    st.write(f"**Submitter:** {req['submitter']}")
    st.write(f"**Created:** {req['created_at']}")
    st.write(f"**Last Updated:** {req['updated_at']}")
    
    st.divider()
    
    # Status Update (Dev/Admin)
    if st.session_state.get("role") in ["Developer", "Admin"]:
        st.subheader("Update Status")
        new_status = st.selectbox("New Status", ["Open", "In Progress", "Clarification Needed", "Implemented", "Closed"], index=["Open", "In Progress", "Clarification Needed", "Implemented", "Closed"].index(req['status']))
        if st.button("Update Status"):
            update_requirement_status(req_id, new_status)
            st.success("Status updated!")
            st.rerun()

    st.divider()
    
    # Edit Logic
    if st.session_state.get("role") in ["Developer", "Admin"] or st.session_state.get("user") == req['submitter']:
        with st.expander("Edit Details"):
            with st.form("edit_req_form"):
                new_remarks = st.text_area("Update Remarks", value=req['remarks'])
                new_type = st.selectbox("Update Type", ["Design Change", "Feature Change", "New Requirement", "Bug Fix", "Other"], index=["Design Change", "Feature Change", "New Requirement", "Bug Fix", "Other"].index(req['requirement_type']))
                
                # Manage Assets
                st.caption("Manage Assets")
                current_assets = req['assets_paths'].split(',') if req.get('assets_paths') else []
                assets_to_keep = st.multiselect("Keep Assets (Uncheck to Remove)", current_assets, default=current_assets, format_func=os.path.basename)
                new_assets = st.file_uploader("Add New Assets", accept_multiple_files=True, key="new_assets_edit")

                if st.form_submit_button("Save Changes"):
                    # Handle New Assets
                    final_asset_paths = assets_to_keep
                    if new_assets:
                        upload_dir = "app/uploads/requirements/assets"
                        os.makedirs(upload_dir, exist_ok=True)
                        for asset in new_assets:
                            file_path = os.path.join(upload_dir, f"{req_id}_asset_{asset.name}")
                            with open(file_path, "wb") as f:
                                f.write(asset.getbuffer())
                            final_asset_paths.append(file_path)
                    
                    update_requirement_details(req_id, new_remarks, new_type, req['current_design_path'], req['reference_img_path'], ",".join(final_asset_paths))
                    st.success("Updated!")
                    st.rerun()

st.page_link("pages/requirement_dashboard.py", label="Back to Dashboard", icon="🔙")
