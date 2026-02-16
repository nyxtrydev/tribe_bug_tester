import streamlit as st
from database import get_pending_users, approve_user
from auth import admin_create_user, try_auto_login

st.set_page_config(page_title="Admin Panel", page_icon="🛡️", layout="wide", initial_sidebar_state="expanded")

try_auto_login()

if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("Please log in to access this page.")
    st.stop()

if st.session_state.get("role") != "Admin":
    st.error("Access Denied. Admins only.")
    st.stop()

st.title("🛡️ Admin Panel")

tab1, tab2 = st.tabs(["Pending Approvals", "Create User"])

with tab1:
    st.subheader("Pending User Approvals")
    pending = get_pending_users()
    
    if not pending:
        st.info("No pending users.")
    else:
        for user in pending:
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"**{user['username']}** ({user['role']})")
            with col2:
                if st.button("Approve", key=f"approve_{user['username']}"):
                    approve_user(user['username'])
                    st.success(f"Approved {user['username']}")
                    st.rerun()

with tab2:
    st.subheader("Create New User")
    with st.form("admin_create_user"):
        new_user = st.text_input("Username")
        new_pass = st.text_input("Password", type="password")
        new_role = st.selectbox("Role", ["Tester", "Developer", "Admin"])
        
        if st.form_submit_button("Create User"):
            if new_user and new_pass:
                success, msg = admin_create_user(new_user, new_pass, new_role)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)
            else:
                st.warning("Username and Password are required")
