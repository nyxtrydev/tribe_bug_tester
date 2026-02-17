import streamlit as st
from auth import logout, get_manager

def render_sidebar():
    """Renders the custom sidebar navigation."""
    # Sidebar
    st.sidebar.title(f"User: {st.session_state.get('user', 'Guest')}")
    st.sidebar.caption(f"Role: {st.session_state.get('role', 'Unknown')}")
    
    st.sidebar.page_link("app.py", label="Home", icon="🏠")
    st.sidebar.page_link("pages/dashboard.py", label="Dashboard", icon="📊")
    st.sidebar.page_link("pages/submit_issue.py", label="Submit Issue", icon="📝")
    # st.sidebar.page_link("pages/issue_detail.py", label="Issue Details", icon="📄")
    
    st.sidebar.divider()
    st.sidebar.caption("Design Updates")
    st.sidebar.page_link("pages/design_dashboard.py", label="Design Dashboard", icon="🎨")
    st.sidebar.page_link("pages/submit_design.py", label="Submit Design", icon="🖌️")

    st.sidebar.divider()
    st.sidebar.caption("Requirements")
    st.sidebar.page_link("pages/requirement_dashboard.py", label="Req. Dashboard", icon="📊")
    st.sidebar.page_link("pages/submit_requirement.py", label="Submit Req.", icon="📝")
    
    # Admin Panel Link if Admin
    st.sidebar.divider()
    if st.session_state.get("role") == "Admin":
         st.sidebar.page_link("pages/admin_panel.py", label="Admin Panel", icon="🛡️")

    st.sidebar.divider()
    if st.sidebar.button("Logout"):
        cookie_manager = get_manager()
        logout(cookie_manager)
