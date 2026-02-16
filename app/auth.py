import bcrypt
import streamlit as st
from database import get_user, init_db, create_user

def check_password(plain_text, hashed_text):
    return bcrypt.checkpw(plain_text.encode('utf-8'), hashed_text.encode('utf-8'))

def login_user(username, password):
    user = get_user(username)
    if user:
        if check_password(password, user['password_hash']):
            return user
    return None

def register_user(username, password, role):
    if get_user(username):
        return False, "Username already exists"
    
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    if create_user(username, hashed, role):
        return True, "User created successfully"
    return False, "Database error"

def logout():
    st.session_state['logged_in'] = False
    st.session_state['user'] = None
    st.session_state['role'] = None
    st.rerun()

def require_auth():
    if "logged_in" not in st.session_state or not st.session_state['logged_in']:
        st.warning("Please log in to access this page.")
        st.stop()
