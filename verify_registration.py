import sys
import os

# Add app directory to path
sys.path.append(os.path.join(os.getcwd(), 'app'))

from database import init_db, get_user
from auth import register_user, login_user

def run_registration_test():
    print("--- Starting Registration Verification ---")
    
    # 1. Initialize DB
    print("1. Initializing DB...")
    init_db()

    # 2. Test Registration
    print("2. Testing Registration (New User)...")
    username = "testuser"
    password = "testpassword"
    role = "Member"
    
    # Clean up if exists (for re-runnability)
    # Ideally we'd have a delete_user function or use a test DB, but standard flow handles "already exists"
    
    success, msg = register_user(username, password, role)
    if success:
        print(f"   ✅ Registration Successful: {msg}")
    elif msg == "Username already exists":
        print(f"   ℹ️ User already exists (Expected if re-running): {msg}")
    else:
        print(f"   ❌ Registration Failed: {msg}")
        return

    # 3. Test Login with New User
    print("3. Testing Login with New User...")
    user = login_user(username, password)
    if user and user['username'] == username and user['role'] == role:
        print("   ✅ Login Successful.")
    else:
        print("   ❌ Login Failed.")

    print("--- Verification Complete ---")

if __name__ == "__main__":
    run_registration_test()
