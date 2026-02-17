import streamlit as st
import time
from database import init_db
from auth import login_user, logout, register_user, get_manager, get_user, try_auto_login

st.set_page_config(page_title="QA Issue Tracker", page_icon="🐞", layout="wide", initial_sidebar_state="expanded")

# Initialize DB
init_db()

# Session State for Auth
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["user"] = None
    st.session_state["role"] = None

from auth import get_manager, get_user, try_auto_login

# Initialize Cookie Manager
cookie_manager = get_manager()

# Try Auto-Login
if try_auto_login():
    st.success(f"Welcome back, {st.session_state['user']}!")

def login_page():
    st.title("🐞 Internal QA Issue Tracker")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        st.subheader("Login")
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        
        if st.button("Login"):
            user, error = login_user(username, password, cookie_manager)
            if user:
                st.session_state["logged_in"] = True
                st.session_state["user"] = user['username']
                st.session_state["role"] = user['role']
                st.success("Logged in successfully!")
                time.sleep(0.5) # Give cookie a moment
                st.rerun()
            else:
                st.error(error)

    with tab2:
        st.subheader("Create Account")
        new_user = st.text_input("Username", key="new_user")
        new_pass = st.text_input("Password", type="password", key="new_pass")
        role = st.selectbox("Role", ["Tester", "Developer"], key="new_role")
        
        if st.button("Sign Up"):
            if new_user and new_pass:
                success, msg = register_user(new_user, new_pass, role)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)
            else:
                st.warning("Username and Password are required")

def main():
    if not st.session_state["logged_in"]:
        login_page()
        return

    # Sidebar
    from navigation import render_sidebar
    render_sidebar()

    st.title("Welcome to the QA Tracker")
    st.markdown("""
    Use the sidebar to navigate:
    - **Dashboard**: View and filter existing issues.
    - **Submit Issue**: Report a new bug or improvement.
    - **Issue Details**: Deep dive into specific issues.
    """)

if __name__ == "__main__":
    main()
