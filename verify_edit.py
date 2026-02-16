import sys
import os
import datetime

# Add app directory to path
sys.path.append(os.path.join(os.getcwd(), 'app'))

from database import init_db, create_issue, get_issue_by_id, update_issue_details

def run_edit_test():
    print("--- Starting Edit Issue Verification ---")
    
    # 1. Initialize DB
    init_db()

    # 2. Create Dummy Issue
    issue_id = "EDIT-TEST-01"
    create_issue({
        "id": issue_id,
        "submitter": "tester",
        "account_type": "Member",
        "issue_type": "Bug",
        "screen_name": "Home",
        "title": "Edit Test",
        "description": "Original Description",
        "severity": "Low", 
        "steps_to_reproduce": "Original Steps",
        "expected_result": "Original Expected",
        "actual_result": "Original Actual",
        "file_paths": ""
    })
    
    # 3. Update Issue
    print("3. Updating Issue Details...")
    update_issue_details(issue_id, "New Steps", "New Expected", "New Actual")
    
    # 4. Verify Update
    print("4. Verifying Update...")
    issue = get_issue_by_id(issue_id)
    
    if issue:
        if (issue['steps_to_reproduce'] == "New Steps" and 
            issue['expected_result'] == "New Expected" and 
            issue['actual_result'] == "New Actual"):
            print("   ✅ Issue details updated successfully.")
        else:
            print(f"   ❌ Update failed. Got: {issue['steps_to_reproduce']}, {issue['expected_result']}, {issue['actual_result']}")
    else:
        print("   ❌ Issue not found.")

    print("--- Verification Complete ---")

if __name__ == "__main__":
    run_edit_test()
