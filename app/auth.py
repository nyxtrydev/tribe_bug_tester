import bcrypt
import streamlit as st
import datetime
from database import get_user, init_db, create_user

def check_password(plain_text, hashed_text):
    return bcrypt.checkpw(plain_text.encode('utf-8'), hashed_text.encode('utf-8'))

import extra_streamlit_components as stx

def get_manager(key="init"):
    return stx.CookieManager(key=key)

def login_user(username, password, cookie_manager):
    user = get_user(username)
    if user:
        if check_password(password, user['password_hash']):
            if user['is_approved']:
                # Set Cookie
                try:
                    cookie_manager.set("auth_token", username, expires_at=datetime.datetime.now() + datetime.timedelta(days=7))
                except Exception as e:
                    print(f"Cookie set error: {e}")
                return user, None
            else:
                return None, "Account pending approval."
    return None, "Invalid username or password"

def try_auto_login():
    """Checks for auth_token cookie and logs user in if valid."""
    apply_custom_style()
    
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
        st.session_state["user"] = None
        st.session_state["role"] = None

    if not st.session_state["logged_in"]:
        cookie_manager = get_manager(key="auto_login")
        auth_token = cookie_manager.get(cookie="auth_token")
        
        if auth_token:
            user = get_user(auth_token)
            if user:
                st.session_state["logged_in"] = True
                st.session_state["user"] = user['username']
                st.session_state["role"] = user['role']
                # return True to indicate successful auto-login
                return True
    return False

def apply_custom_style():
    st.markdown("""
        <style>
            /* Hide Streamlit Toolbar items (Menu, Share, etc.) */
            div[data-testid="stToolbar"] {
                display: none !important;
            }
            
            /* Hide the decoration line at the top */
            div[data-testid="stDecoration"] {
                display: none !important;
            }
            
            /* Hide the footer */
            footer {
                display: none !important;
            }
            
            /* Ensure the sidebar toggle (hamburger) is visible and accessible */
            button[kind="header"] {
                visibility: visible !important;
            }
            
            /* Make sure sidebar itself is not hidden */
            section[data-testid="stSidebar"] {
                visibility: visible !important;
            }
        </style>
        """, unsafe_allow_html=True)

def register_user(username, password, role):
    if get_user(username):
        return False, "Username already exists"
    
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    # Default is_approved=False for public registration
    if create_user(username, hashed, role, is_approved=False):
        return True, "Account created! Waiting for Admin approval."
    return False, "Database error"

def admin_create_user(username, password, role):
    if get_user(username):
        return False, "Username already exists"
    
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    # Admin created users are approved by default
    if create_user(username, hashed, role, is_approved=True):
        return True, "User created successfully"
    return False, "Database error"

def logout(cookie_manager):
    st.session_state['logged_in'] = False
    st.session_state['user'] = None
    st.session_state['role'] = None
    
    # Delete Cookie
    try:
        cookie_manager.delete("auth_token")
    except Exception as e:
        print(f"Cookie delete error: {e}")
    
    st.rerun()



def require_auth():
    if "logged_in" not in st.session_state or not st.session_state['logged_in']:
        st.warning("Please log in to access this page.")
        st.stop()
