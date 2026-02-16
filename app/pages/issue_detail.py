import streamlit as st
import os
from database import get_issue_by_id, get_auto_test_results, add_comment, get_comments, update_status, delete_issue


st.set_page_config(page_title="Issue Details", page_icon="📄", layout="wide")

if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("Please log in to access this page.")
    st.stop()

if "selected_issue_id" not in st.session_state or not st.session_state["selected_issue_id"]:
    st.warning("No issue selected. Please go to the Dashboard to select an issue.")
    st.page_link("pages/dashboard.py", label="Go to Dashboard", icon="📊")
    st.stop()

issue_id = st.session_state["selected_issue_id"]
issue = get_issue_by_id(issue_id)

if not issue:
    st.error("Issue not found!")
    st.stop()

st.title(f"📄 {issue['title']}")
st.caption(f"ID: {issue['id']} | Submitted by: {issue['submitter']} | Created: {issue['created_at']}")

# Layout
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Description")
    st.write(issue['description'])
    
    with st.expander("Details (Steps, Expected, Actual)", expanded=False):
        st.markdown(f"**Steps to Reproduce:**\n{issue['steps_to_reproduce'] or 'N/A'}")
        st.markdown(f"**Expected Result:**\n{issue['expected_result'] or 'N/A'}")
        st.markdown(f"**Actual Result:**\n{issue['actual_result'] or 'N/A'}")

    st.subheader("Attachments")
    if issue['file_paths']:
        paths = issue['file_paths'].split(',')
        for path in paths:
            if os.path.exists(path):
                # Check extension to decide how to render
                ext = os.path.splitext(path)[1].lower()
                if ext in ['.png', '.jpg', '.jpeg']:
                    st.image(path, caption=os.path.basename(path), width=400)
                elif ext in ['.mp4', '.webm']:
                    st.video(path)
                else:
                    st.markdown(f"[{os.path.basename(path)}]({path})")
            else:
                st.warning(f"File not found: {path}")
    else:
        st.info("No attachments.")

    st.divider()
    st.subheader("Comments")
    comments = get_comments(issue_id)
    for c in comments:
        st.markdown(f"**{c['username']}** ({c['created_at']}): {c['comment']}")
    
    new_comment = st.text_area("Add a comment")
    if st.button("Post Comment"):
        if new_comment:
            add_comment(issue_id, st.session_state['user'], new_comment)
            st.success("Comment added!")
            st.rerun()

with col2:
    st.subheader("Status & Metadata")
    current_status = issue['status']
    
    # RBAC for Status
    user_role = st.session_state.get('role', 'Tester')
    
    if user_role == 'Admin':
        status_options = ["Open", "In Progress", "Fixed", "Closed"]
    elif user_role == 'Developer':
        status_options = ["Open", "In Progress", "Fixed"]
    else: # Tester
        status_options = ["Open", "Closed"]
        
    # Ensure current status is in options (or add it temporarily to avoid error)
    if current_status not in status_options:
        status_options.append(current_status)
        
    new_status = st.selectbox("Status", status_options, index=status_options.index(current_status))
    
    if new_status != current_status:
        if st.button("Update Status"):
            update_status(issue_id, new_status)
            st.success(f"Status updated to {new_status}")
            st.rerun()

    # Admin Only: Delete Issue
    if user_role == 'Admin':
        st.divider()
        if st.button("🗑️ Delete Issue", type="primary"):
            delete_issue(issue_id)
            st.warning("Issue Deleted!")
            st.session_state["selected_issue_id"] = None
            st.switch_page("pages/dashboard.py")
            
    st.info(f"**Severity:** {issue['severity']}")
    st.info(f"**Account Type:** {issue['account_type']}")
    st.info(f"**Issue Type:** {issue['issue_type']}")
    st.info(f"**Screen:** {issue['screen_name']}")

    st.divider()
    st.subheader("🤖 Auto-Test Results")
    results = get_auto_test_results(issue_id)
    if results:
        st.metric("QA Completeness Score", f"{results['qa_score']}/100")
        
        if results['duplicate_score'] > 0.6:
             st.warning(f"⚠️ Potential Duplicate")
        
        st.write(f"**Suggested Severity:** {results['suggested_severity']}")
        
        if results['missing_info'] != "None":
            st.warning(f"Missing: {results['missing_info']}")
    else:
        st.info("No auto-test results available.")
