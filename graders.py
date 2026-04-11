"""
Graders for Code Review Assistant
Each grader returns a score strictly between 0 and 1 (not inclusive)
"""

def grade_easy(prediction):
    """
    Grade syntax error detection
    Returns score between 0.01 and 0.99
    """
    issue = prediction.get("issue", "") if prediction.get("issue") else ""
    issue_lower = issue.lower()
    
    # Start with base score - NEVER 0.0
    score = 0.15
    
    if "missing" in issue_lower and ("parenthesis" in issue_lower or "colon" in issue_lower):
        score = 0.85
    elif "syntax" in issue_lower:
        score = 0.75
    elif "error" in issue_lower:
        score = 0.65
    elif "print" in issue_lower:
        score = 0.55
    elif issue:
        score = 0.45
    else:
        score = 0.25
    
    # Ensure score is NEVER 0.0 or 1.0
    if score >= 0.99:
        score = 0.98
    if score <= 0.01:
        score = 0.02
    
    return score


def grade_medium(prediction):
    """
    Grade runtime bug detection
    Returns score between 0.01 and 0.99
    """
    issue = prediction.get("issue", "") if prediction.get("issue") else ""
    issue_lower = issue.lower()
    
    # Start with base score - NEVER 0.0
    score = 0.15
    
    if "index" in issue_lower and ("out of range" in issue_lower or "out of bounds" in issue_lower):
        score = 0.85
    elif "index" in issue_lower:
        score = 0.70
    elif "range" in issue_lower or "bound" in issue_lower:
        score = 0.60
    elif "array" in issue_lower:
        score = 0.50
    elif issue:
        score = 0.40
    else:
        score = 0.25
    
    # Ensure score is NEVER 0.0 or 1.0
    if score >= 0.99:
        score = 0.98
    if score <= 0.01:
        score = 0.02
    
    return score


def grade_hard(prediction):
    """
    Grade security vulnerability detection
    Returns score between 0.01 and 0.99
    """
    issue = prediction.get("issue", "") if prediction.get("issue") else ""
    issue_lower = issue.lower()
    
    # Start with base score - NEVER 0.0
    score = 0.15
    
    if "sql injection" in issue_lower:
        score = 0.88
    elif "injection" in issue_lower:
        score = 0.78
    elif "sql" in issue_lower or "query" in issue_lower:
        score = 0.68
    elif "vulnerability" in issue_lower:
        score = 0.58
    elif "security" in issue_lower:
        score = 0.48
    elif issue:
        score = 0.38
    else:
        score = 0.25
    
    # Ensure score is NEVER 0.0 or 1.0
    if score >= 0.99:
        score = 0.98
    if score <= 0.01:
        score = 0.02
    
    return score


# CRITICAL: This dictionary MUST exist and have these exact keys
GRADERS = {
    "easy": grade_easy,
    "medium": grade_medium,
    "hard": grade_hard
}

# Also export as TASK_GRADERS for compatibility
TASK_GRADERS = GRADERS

# For OpenEnv compatibility
OPENENV_GRADERS = GRADERS
