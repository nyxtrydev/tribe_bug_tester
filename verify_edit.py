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
    
    # 4. Verify Update and Re-diagnosis
    print("4. Verifying Update and Re-diagnosis...")
    issue = get_issue_by_id(issue_id)
    
    # Check if diagnostics were re-run
    # In a real app we'd check the DB, but here we can check if the 'missing_info' field in auto_test_results is updated.
    # We need to import get_auto_test_results
    from database import get_auto_test_results
    results = get_auto_test_results(issue_id)
    
    if issue:
        if (issue['steps_to_reproduce'] == "New Steps" and 
            issue['expected_result'] == "New Expected" and 
            issue['actual_result'] == "New Actual"):
            print("   ✅ Issue details updated successfully.")
            
            # Since "New Steps" is short (<10 chars), it should still have a warning about being short.
            # But let's say we update it to something long enough to clear the warning.
            
            if results:
                 print(f"   ℹ️ QA Score: {results['qa_score']}")
                 print(f"   ℹ️ Missing Info: {results['missing_info']}")
            else:
                 print("   ❌ No auto-test results found.")
                 
        else:
            print(f"   ❌ Update failed. Got: {issue['steps_to_reproduce']}, {issue['expected_result']}, {issue['actual_result']}")
    else:
        print("   ❌ Issue not found.")

    print("--- Verification Complete ---")

if __name__ == "__main__":
    run_edit_test()
