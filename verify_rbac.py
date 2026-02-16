import sys
import os

# Add app directory to path
sys.path.append(os.path.join(os.getcwd(), 'app'))

from database import init_db, get_user, create_issue, delete_issue, get_issue_by_id
from auth import login_user

def run_rbac_test():
    print("--- Starting RBAC Verification ---")
    
    # 1. Initialize DB (Creates Super Admin)
    print("1. Initializing DB...")
    init_db()

    # 2. Test Super Admin Login
    print("2. Testing Super Admin (abhiraman)...")
    user = login_user("abhiraman", "123456@")
    if user and user['role'] == 'Admin':
        print("   ✅ Super Admin Login Successful.")
    else:
        print("   ❌ Super Admin Login Failed.")
        return

    # 3. Test Delete Issue (Admin Only)
    print("3. Testing Delete Issue (DB function)...")
    # Create temp issue
    issue_id = "DELETE-TEST-01"
    issue_data = {
        "id": issue_id,
        "submitter": "abhiraman",
        "account_type": "Owner",
        "issue_type": "Bug",
        "screen_name": "Test",
        "title": "To Delete",
        "description": "Delete me",
        "severity": "Low", 
        "file_paths": ""
    }
    create_issue(issue_data)
    
    if get_issue_by_id(issue_id):
        print("   ✅ Temporary issue created.")
        delete_issue(issue_id)
        if not get_issue_by_id(issue_id):
            print("   ✅ Issue deleted successfully.")
        else:
            print("   ❌ Failed to delete issue.")
    else:
        print("   ❌ Failed to create temp issue.")

    print("--- Verification Complete ---")

if __name__ == "__main__":
    run_rbac_test()
