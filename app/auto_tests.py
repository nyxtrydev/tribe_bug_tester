from difflib import SequenceMatcher
from database import get_all_issues

def check_duplicate(title, description):
    """
    Check for potential duplicates based on title and description similarity.
    Returns a score (0.0 to 1.0) and a potential duplicate issue ID.
    """
    existing_issues = get_all_issues()
    max_score = 0.0
    duplicate_id = None

    text = f"{title} {description}".lower()

    for issue in existing_issues:
        existing_text = f"{issue['title']} {issue['description']}".lower()
        score = SequenceMatcher(None, text, existing_text).ratio()
        if score > max_score:
            max_score = score
            duplicate_id = issue['id']

    return max_score, duplicate_id

def suggest_severity(title, description):
    """
    Suggest severity based on keywords.
    """
    text = f"{title} {description}".lower()
    
    critical_keywords = ['crash', 'exception', '500', 'security', 'data loss', 'freeze']
    high_keywords = ['login failed', 'broken', 'not working', 'timeout', 'slow']
    
    for kw in critical_keywords:
        if kw in text:
            return "Critical"
    
    for kw in high_keywords:
        if kw in text:
            return "High"
            
    return "Medium" # Default

def check_missing_info(steps, expected, actual):
    warnings = []
    if not steps or len(steps) < 10:
        warnings.append("Steps to reproduce are missing or too short.")
    if not expected:
        warnings.append("Expected result is missing.")
    if not actual:
        warnings.append("Actual result is missing.")
    return warnings

def calculate_qa_score(missing_info_count, duplicate_score, has_screenshots):
    """
    Calculate a 0-100 QA score.
    """
    score = 100
    
    # Deduct for missing info
    score -= (missing_info_count * 15)
    
    # Deduct for potential duplicate
    if duplicate_score > 0.8:
        score -= 50
    elif duplicate_score > 0.5:
        score -= 20
        
    # Bonus for screenshots
    if has_screenshots:
        score += 10
        
    return max(0, min(100, score))


def run_diagnostics(title, description, steps, expected, actual, file_paths):
    duplicate_score, duplicate_id = check_duplicate(title, description)
    severity = suggest_severity(title, description)
    missing_warnings = check_missing_info(steps, expected, actual)
    
    qa_score = calculate_qa_score(len(missing_warnings), duplicate_score, bool(file_paths))

    return {
        "duplicate_score": duplicate_score,
        "duplicate_id": duplicate_id,
        "suggested_severity": severity,
        "missing_info": ", ".join(missing_warnings) if missing_warnings else "None",
        "qa_score": qa_score
    }
