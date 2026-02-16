import sys
import os

# Add app directory to path
sys.path.append(os.path.join(os.getcwd(), 'app'))

from database import init_db, get_user, approve_user
from auth import login_user, register_user, admin_create_user

def run_approval_test():
    print("--- Starting User Approval Verification ---")
    
    # 1. Initialize DB (Updates Super Admin)
    print("1. Initializing DB...")
    init_db()

    # 2. Register New User (Pending)
    username = "new_tester"
    password = "password123"
    print(f"2. Registering '{username}'...")
    success, msg = register_user(username, password, "Tester")
    if success:
        print(f"   ✅ Registered: {msg}")
    elif msg == "Username already exists":
        print(f"   ℹ️ User exists, proceeding.")
    else:
        print(f"   ❌ Registration failed: {msg}")

    # 3. Try Login (Should Fail)
    print("3. Attempting Login (Should fail due to pending)...")
    user, error = login_user(username, password)
    if user:
         print("   ❌ Login succeeded unexpectedly!")
    else:
         print(f"   ✅ Login failed as expected: {error}")

    # 4. Super Admin Check
    print("4. Checking Super Admin Login...")
    admin_user, admin_err = login_user("abhiraman", "Tribe#123#@")
    if admin_user:
        print("   ✅ Super Admin login successful.")
    else:
        print(f"   ❌ Super Admin login failed: {admin_err}")

    # 5. Approve User
    print(f"5. Approving '{username}'...")
    approve_user(username)
    
    # 6. Try Login Again (Should Succeed)
    print("6. Attempting Login Again...")
    user, error = login_user(username, password)
    if user:
         print("   ✅ Login successful!")
    else:
         print(f"   ❌ Login failed: {error}")

    # 7. Admin Create User
    print("7. Testing Admin Create User...")
    dev_user = "admin_created_dev"
    success, msg = admin_create_user(dev_user, "devpass123", "Developer")
    if success:
        print(f"   ✅ Admin Creation: {msg}")
        # Verify login immediately
        u, e = login_user(dev_user, "devpass123")
        if u:
            print("   ✅ Created user can login immediately.")
        else:
             print(f"   ❌ Created user cannot login: {e}")
    elif msg == "Username already exists":
         print("   ℹ️ User exists.")
    else:
        print(f"   ❌ Admin creation failed: {msg}")

    print("--- Verification Complete ---")

if __name__ == "__main__":
    run_approval_test()
