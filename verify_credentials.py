import sys
import os

# Add app directory to path
sys.path.append(os.path.join(os.getcwd(), 'app'))

from database import init_db, create_issue, get_issue_by_id

def run_credentials_test():
    print("--- Starting Test Credentials Verification ---")
    
    # 1. Initialize DB (Triggers Migration)
    print("1. Initializing DB (Check for migration message)...")
    init_db()

    # 2. Create Issue with Credentials
    print("2. Creating Issue with Credentials...")
    issue_id = "CRED-TEST-01"
    issue_data = {
        "id": issue_id,
        "submitter": "abhiraman",
        "account_type": "Member",
        "issue_type": "Bug",
        "screen_name": "Login",
        "title": "Credential Test",
        "description": "Testing extra fields",
        "severity": "Low", 
        "file_paths": "",
        "test_username": "bug_user",
        "test_password": "bug_password",
        "test_email": "bug@example.com"
    }
    
    create_issue(issue_data)
    
    # 3. Verify Retrieval
    print("3. Verifying Retrieval...")
    issue = get_issue_by_id(issue_id)
    
    if issue:
        print(f"   Issue Found: {issue['title']}")
        # Check if keys exist and match (sqlite Row acts like dict but need to be sure column exists)
        try:
            if (issue['test_username'] == "bug_user" and 
                issue['test_password'] == "bug_password" and 
                issue['test_email'] == "bug@example.com"):
                print("   ✅ Credentials stored and retrieved successfully.")
            else:
                print(f"   ❌ Credentials mismatch: {dict(issue)}")
        except IndexError:
             print("   ❌ Columns not found in result row.")
    else:
        print("   ❌ Issue not found.")

    print("--- Verification Complete ---")

if __name__ == "__main__":
    run_credentials_test()
