import streamlit as st
import os
import uuid
import datetime
import uuid
import datetime
from database import create_issue, save_auto_test_results, get_recent_test_credentials
from auto_tests import run_diagnostics

st.set_page_config(page_title="Submit Issue", page_icon="📝", layout="wide", initial_sidebar_state="expanded")

from auth import try_auto_login
try_auto_login()

from navigation import render_sidebar
render_sidebar()

if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("Please log in to access this page.")
    st.stop()

st.title("📝 Submit New Issue")

with st.form("issue_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        account_type = st.selectbox("Account Type", ["Owner", "Trainer", "Member"])
        issue_type = st.selectbox("Issue Type", ["Bug", "UI Issue", "Performance", "Feature Not Working", "UI Improvement", "Other"])
        screen_name = st.text_input("Screen/Page Name")
        title = st.text_input("Issue Title")
    
    with col2:
        severity = st.selectbox("Severity", ["Critical", "High", "Medium", "Low"])
        
    description = st.text_area("Issue Description")
    steps = st.text_area("Steps to Reproduce (Optional)")
    expected = st.text_area("Expected Result (Optional)")
    actual = st.text_area("Actual Result (Optional)")
    
    st.subheader("Test Credentials (Optional)")
    
    # Quick Fill Logic
    recent_creds = get_recent_test_credentials()
    recent_options = ["None (Type New)"] + [f"{c['test_username']} / {c['test_password']}" for c in recent_creds]
    
    # We use session state to populate the fields if a selection is made
    # But text_input defaults only work on first render or re-render. 
    # To make it dynamic, we can use an on_change handler or just check the value of the selectbox.
    
    selected_cred_str = st.selectbox("⚡ Quick Fill from Recent", recent_options, key="quick_fill_key")
    
    default_user, default_pass, default_email = "", "", ""
    if selected_cred_str != "None (Type New)":
        # Find the matching credential object
        for c in recent_creds:
            if f"{c['test_username']} / {c['test_password']}" == selected_cred_str:
                default_user = c['test_username']
                default_pass = c['test_password']
                default_email = c['test_email']
                break
    
    c1, c2, c3 = st.columns(3)
    with c1:
        test_user = st.text_input("Test Username", value=default_user)
    with c2:
        test_pass = st.text_input("Test Password", value=default_pass)
    with c3:
        test_email = st.text_input("Test Email", value=default_email)
    
    
    uploaded_files = st.file_uploader("Upload Screenshots/Designs/Recordings", accept_multiple_files=True)
    
    submitted = st.form_submit_button("Submit Issue")
    
    if submitted:
        if not title or not description:
            st.error("Title and Description are required.")
        else:
            issue_id = f"BUG-{uuid.uuid4().hex[:6].upper()}"
            
            # Save files
            saved_file_paths = []
            if uploaded_files:
                upload_dir = "app/uploads" 
                for uploaded_file in uploaded_files:
                    file_path = os.path.join(upload_dir, f"{issue_id}_{uploaded_file.name}")
                    # Ensure directory exists
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    saved_file_paths.append(file_path)
            
            # Run diagnostics
            diagnostics = run_diagnostics(title, description, steps, expected, actual, saved_file_paths)
            
            # Create Issue Data
            issue_data = {
                "id": issue_id,
                "submitter": st.session_state["user"],
                "account_type": account_type,
                "issue_type": issue_type,
                "screen_name": screen_name,
                "title": title,
                "description": description,
                "steps_to_reproduce": steps,
                "expected_result": expected,
                "actual_result": actual,
                "severity": severity,
                "severity": severity,
                "file_paths": ",".join(saved_file_paths),
                "test_username": test_user,
                "test_password": test_pass,
                "test_email": test_email
            }
            
            create_issue(issue_data)
            save_auto_test_results(issue_id, diagnostics)
            
            st.success(f"Issue {issue_id} submitted successfully!")
            
            # Optional: If you want to force clear the select box for next run
            # st.session_state["quick_fill_key"] = "None (Type New)" # Cause Crash
            
            # Show diagnostic feedback immediately
            with st.expander("Auto-Test Diagnostics Report", expanded=True):
                st.write(f"**QA Score:** {diagnostics['qa_score']}/100")
                if diagnostics['duplicate_score'] > 0.6:
                    st.warning(f"⚠️ Potential Duplicate Detected (ID: {diagnostics['duplicate_id']})")
                if diagnostics['suggested_severity'] != severity:
                    st.info(f"ℹ️ Suggested Severity: **{diagnostics['suggested_severity']}** (You selected {severity})")
                if diagnostics['missing_info'] != "None":
                    st.warning(f"⚠️ Missing Info: {diagnostics['missing_info']}")
