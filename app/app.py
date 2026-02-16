import streamlit as st
from database import init_db
from auth import login_user, logout, register_user

st.set_page_config(page_title="QA Issue Tracker", page_icon="🐞", layout="wide")

# Initialize DB
init_db()

# Session State for Auth
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["user"] = None
    st.session_state["role"] = None

def login_page():
    st.title("🐞 Internal QA Issue Tracker")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        st.subheader("Login")
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        
        if st.button("Login"):
            user = login_user(username, password)
            if user:
                st.session_state["logged_in"] = True
                st.session_state["user"] = user['username']
                st.session_state["role"] = user['role']
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid username or password")
        

                
    with tab2:
        st.subheader("Create Account")
        new_user = st.text_input("Username", key="new_user")
        new_pass = st.text_input("Password", type="password", key="new_pass")
        role = st.selectbox("Role", ["Tester", "Developer"], key="new_role")
        
        if st.button("Sign Up"):
            if new_user and new_pass:
                success, msg = register_user(new_user, new_pass, role)
                if success:
                    st.success("Account created! Please log in.")
                else:
                    st.error(msg)
            else:
                st.warning("Username and Password are required")

def main():
    if not st.session_state["logged_in"]:
        login_page()
        return

    # Sidebar
    st.sidebar.title(f"User: {st.session_state['user']}")
    st.sidebar.caption(f"Role: {st.session_state['role']}")
    
    st.sidebar.page_link("app.py", label="Home", icon="🏠")
    st.sidebar.page_link("pages/dashboard.py", label="Dashboard", icon="📊")
    st.sidebar.page_link("pages/submit_issue.py", label="Submit Issue", icon="📝")
    st.sidebar.page_link("pages/issue_detail.py", label="Issue Details", icon="📄")
    
    st.sidebar.divider()
    if st.sidebar.button("Logout"):
        logout()

    st.title("Welcome to the QA Tracker")
    st.markdown("""
    Use the sidebar to navigate:
    - **Dashboard**: View and filter existing issues.
    - **Submit Issue**: Report a new bug or improvement.
    - **Issue Details**: Deep dive into specific issues.
    """)

if __name__ == "__main__":
    main()
