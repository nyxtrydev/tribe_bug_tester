import streamlit as st
import os
from database import get_design_request_by_id, update_design_request_status, update_design_request_details
from auth import try_auto_login

st.set_page_config(page_title="Design Request Details", page_icon="🎨", layout="wide", initial_sidebar_state="expanded")

try_auto_login()

from navigation import render_sidebar
render_sidebar()

if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("Please log in to access this page.")
    st.stop()

if "selected_design_id" not in st.session_state or not st.session_state["selected_design_id"]:
    st.warning("No design request selected.")
    st.stop()

req_id = st.session_state["selected_design_id"]
req = get_design_request_by_id(req_id)

if not req:
    st.error("Design Request not found!")
    st.stop()

st.title(f"🎨 {req['screen_name']}")
st.caption(f"ID: {req['id']} | Submitted by: {req['submitter']} | Created: {req['created_at']}")

# Main Layout
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Details")
    st.markdown(f"**Design References:**\n{req['design_references']}")
    
    # Display Reference Images
    if req['reference_img_paths']:
        st.caption("Reference Images:")
        ref_paths = req['reference_img_paths'].split(',')
        cols = st.columns(2)
        for i, path in enumerate(ref_paths):
            if path and os.path.exists(path):
                cols[i % 2].image(path, caption=os.path.basename(path), use_container_width=True)
    
    st.markdown(f"**Notes:**\n{req['notes']}")
    
    st.divider()
    
    # Edit Section
    with st.expander("Edit Details & Images", expanded=False):
        with st.form("edit_design_form"):
            new_notes = st.text_area("Update Notes", value=req['notes'])
            new_priority = st.selectbox("Update Priority", ["High", "Medium", "Low"], index=["High", "Medium", "Low"].index(req['priority']))
            
            # --- Manage Mocks ---
            st.caption("Manage Design Mocks")
            current_paths = req['file_paths'].split(',') if req['file_paths'] else []
            images_to_keep = st.multiselect("Keep Mocks (Uncheck to Remove)", current_paths, default=current_paths, format_func=os.path.basename)
            new_files = st.file_uploader("Add New Mocks", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'], key="new_mocks")
            
            # --- Manage References ---
            st.divider()
            st.caption("Manage Reference Images")
            current_refs = req['reference_img_paths'].split(',') if req['reference_img_paths'] else []
            refs_to_keep = st.multiselect("Keep References (Uncheck to Remove)", current_refs, default=current_refs, format_func=os.path.basename)
            new_refs = st.file_uploader("Add New References", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'], key="new_refs")
            
            if st.form_submit_button("Save Changes"):
                # Handle Mocks
                final_paths = images_to_keep
                if new_files:
                    upload_dir = "app/uploads/designs" 
                    for uploaded_file in new_files:
                        file_path = os.path.join(upload_dir, f"{req['id']}_mock_{uploaded_file.name}")
                        os.makedirs(os.path.dirname(file_path), exist_ok=True)
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        final_paths.append(file_path)

                # Handle References
                final_ref_paths = refs_to_keep
                if new_refs:
                    ref_dir = "app/uploads/references" 
                    for uploaded_file in new_refs:
                        file_path = os.path.join(ref_dir, f"{req['id']}_ref_{uploaded_file.name}")
                        os.makedirs(os.path.dirname(file_path), exist_ok=True)
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        final_ref_paths.append(file_path)
                
                # Update DB
                update_design_request_details(req_id, new_notes, new_priority, ",".join(final_paths), ",".join(final_ref_paths))
                st.success("Details updated!")
                st.rerun()

    st.subheader("Visuals (Mocks)")
    if req['file_paths']:
        paths = req['file_paths'].split(',')
        if not paths:
             st.info("No images.")
        for path in paths:
            if path and os.path.exists(path):
                st.image(path, caption=os.path.basename(path), width=500)
            elif path: # Path exists in DB but not file
                st.warning(f"File missing: {path}")
    else:
        st.info("No images uploaded.")

with col2:
    st.subheader("Status & Metadata")
    current_status = req['status']
    status_options = ["Open", "In Progress", "Review", "Done"]
    
    if current_status not in status_options:
        status_options.append(current_status)
        
    new_status = st.selectbox("Status", status_options, index=status_options.index(current_status))
    
    if new_status != current_status:
        if st.button("Update Status"):
            update_design_request_status(req_id, new_status)
            st.success(f"Status updated to {new_status}")
            st.rerun()
            
    st.info(f"**Priority:** {req['priority']}")
