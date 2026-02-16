import sys
import os

# Add app directory to path
sys.path.append(os.path.join(os.getcwd(), 'app'))

from database import init_db, create_issue, get_all_issues, get_issue_by_id, update_status, add_comment, get_comments, save_auto_test_results, get_auto_test_results
from auth import login_user
from auto_tests import run_diagnostics

def run_verification():
    print("--- Starting Verification ---")
    
    # 1. Initialize DB
    print("1. Initializing DB...")
    init_db()
    print("   DB Initialized.")

    # 2. Test Auth
    print("2. Testing Auth (Admin Login)...")
    user = login_user("admin", "admin")
    if user and user['username'] == 'admin':
        print("   ✅ Login Successful.")
    else:
        print("   ❌ Login Failed.")
        return

    # 3. Test Issue Creation and Auto-Tests
    print("3. Testing Issue Creation & Auto-Tests...")
    issue_id = "TEST-001"
    
    # Mock data
    file_paths = [] # no files for test
    
    # Run Diagnostics
    diagnostics = run_diagnostics(
        title="App Crashes on Login", 
        description="When I click login, the app freezes and then crashes.", 
        steps="1. Open App. 2. Click Login.", 
        expected="Login", 
        actual="Crash", 
        file_paths=file_paths
    )
    
    issue_data = {
        "id": issue_id,
        "submitter": "admin",
        "account_type": "Owner",
        "issue_type": "Bug",
        "screen_name": "Login Screen",
        "title": "App Crashes on Login",
        "description": "When I click login, the app freezes and then crashes.",
        "steps_to_reproduce": "1. Open App. 2. Click Login.",
        "expected_result": "Login",
        "actual_result": "Crash",
        "severity": "High", # User selected High, but diagnostics should suggest Critical
        "file_paths": ""
    }
    
    create_issue(issue_data)
    save_auto_test_results(issue_id, diagnostics)
    
    # Verify Issue Exists
    issue = get_issue_by_id(issue_id)
    if issue and issue['title'] == "App Crashes on Login":
        print("   ✅ Issue Created Successfully.")
    else:
        print("   ❌ Issue Creation Failed.")

    # Verify Auto-Test Results
    results = get_auto_test_results(issue_id)
    if results and results['suggested_severity'] == "Critical": # "Crash" keyword triggers Critical
        print(f"   ✅ Auto-Test Logic Works (Suggested: {results['suggested_severity']}).")
    else:
        print(f"   ❌ Auto-Test Logic Failed (Got: {results['suggested_severity'] if results else 'None'}).")

    # 4. Test Comments
    print("4. Testing Comments...")
    add_comment(issue_id, "admin", "Investigating this now.")
    comments = get_comments(issue_id)
    if len(comments) == 1 and comments[0]['comment'] == "Investigating this now.":
        print("   ✅ Comment Added Successfully.")
    else:
        print("   ❌ Comment Verification Failed.")

    # 5. Test Status Update
    print("5. Testing Status Update...")
    update_status(issue_id, "In Progress")
    updated_issue = get_issue_by_id(issue_id)
    if updated_issue['status'] == "In Progress":
        print("   ✅ Status Update Successful.")
    else:
        print("   ❌ Status Update Failed.")

    print("--- Verification Complete ---")

if __name__ == "__main__":
    run_verification()
