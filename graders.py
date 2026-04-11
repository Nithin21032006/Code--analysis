def grade_easy(prediction):
    """Grade syntax error detection"""
    issue = prediction.get("issue", "") if prediction.get("issue") else ""
    issue_lower = issue.lower()
    
    if "missing" in issue_lower and ("parenthesis" in issue_lower or "colon" in issue_lower):
        return 0.85
    elif "syntax" in issue_lower:
        return 0.75
    elif "error" in issue_lower:
        return 0.65
    else:
        return 0.45


def grade_medium(prediction):
    """Grade runtime bug detection"""
    issue = prediction.get("issue", "") if prediction.get("issue") else ""
    issue_lower = issue.lower()
    
    if "index" in issue_lower and ("out of range" in issue_lower or "out of bounds" in issue_lower):
        return 0.85
    elif "index" in issue_lower:
        return 0.70
    elif "range" in issue_lower or "bound" in issue_lower:
        return 0.60
    else:
        return 0.45


def grade_hard(prediction):
    """Grade security vulnerability detection"""
    issue = prediction.get("issue", "") if prediction.get("issue") else ""
    issue_lower = issue.lower()
    
    if "sql injection" in issue_lower:
        return 0.88
    elif "injection" in issue_lower:
        return 0.75
    elif "sql" in issue_lower or "query" in issue_lower:
        return 0.65
    else:
        return 0.45


# This is required for the grader references
GRADERS = {
    "grade_easy": grade_easy,
    "grade_medium": grade_medium,
    "grade_hard": grade_hard
}
