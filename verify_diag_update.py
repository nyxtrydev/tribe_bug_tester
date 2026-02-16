import sys
import os
import datetime

# Add app directory to path
sys.path.append(os.path.join(os.getcwd(), 'app'))

from database import init_db, create_issue, get_issue_by_id, update_issue_details, get_auto_test_results, save_auto_test_results
from auto_tests import run_diagnostics

def run_edit_diag_test():
    print("--- Starting Edit & Diagnostics Verification ---")
    
    # 1. Initialize DB
    init_db()

    # 2. Create Issue with Missing Info
    issue_id = "DIAG-TEST-01"
    create_issue({
        "id": issue_id,
        "submitter": "tester",
        "account_type": "Member",
        "issue_type": "Bug",
        "screen_name": "Home",
        "title": "Diag Test",
        "description": "Description",
        "severity": "Low", 
        "steps_to_reproduce": "", # Missing
        "expected_result": "",   # Missing
        "actual_result": "",     # Missing
        "file_paths": ""
    })
    
    # Run initial diagnostics (mimic submit_issue.py)
    diag = run_diagnostics("Diag Test", "Description", "", "", "", [])
    save_auto_test_results(issue_id, diag)
    
    initial_results = get_auto_test_results(issue_id)
    print(f"Initial Missing Info: {initial_results['missing_info']}")
    
    # 3. Update Issue with Complete Info
    print("3. Updating Issue Details...")
    new_steps = "Step 1: Do this. Step 2: Do that. Step 3: Check result." # > 10 chars
    new_expected = "It works."
    new_actual = "It works."
    
    update_issue_details(issue_id, new_steps, new_expected, new_actual)
    
    # 4. Re-run Diagnostics (Mimic issue_detail.py logic)
    print("4. Re-running Diagnostics...")
    new_diag = run_diagnostics("Diag Test", "Description", new_steps, new_expected, new_actual, [])
    save_auto_test_results(issue_id, new_diag)
    
    # 5. Verify Results
    final_results = get_auto_test_results(issue_id)
    print(f"Final Missing Info: {final_results['missing_info']}")
    
    if final_results['missing_info'] == "None":
        print("✅ Diagnostics updated! Missing Info cleared.")
    else:
        print("❌ Diagnostics failed to clear missing info.")

    print("--- Verification Complete ---")

if __name__ == "__main__":
    run_edit_diag_test()
