def grade_easy(prediction):
    """Grade syntax error detection - score STRICTLY between 0 and 1"""
    issue = prediction.get("issue", "").lower() if prediction.get("issue") else ""
    
    # Start with a score that's never 0.0 or 1.0
    score = 0.15
    
    if "missing" in issue and ("parenthesis" in issue or "colon" in issue):
        score = 0.85
    elif "syntax" in issue:
        score = 0.75
    elif "error" in issue:
        score = 0.65
    elif issue:
        score = 0.45
    else:
        score = 0.25
    
    # CRITICAL: Ensure score is NEVER 0.0 or 1.0
    if score >= 0.99:
        score = 0.98
    if score <= 0.01:
        score = 0.02
    
    return score


def grade_medium(prediction):
    """Grade runtime bug detection - score STRICTLY between 0 and 1"""
    issue = prediction.get("issue", "").lower() if prediction.get("issue") else ""
    
    score = 0.15
    
    if "index" in issue and ("out of range" in issue or "out of bounds" in issue):
        score = 0.85
    elif "index" in issue:
        score = 0.70
    elif "range" in issue or "bound" in issue:
        score = 0.60
    elif issue:
        score = 0.45
    else:
        score = 0.25
    
    # CRITICAL: Ensure score is NEVER 0.0 or 1.0
    if score >= 0.99:
        score = 0.98
    if score <= 0.01:
        score = 0.02
    
    return score


def grade_hard(prediction):
    """Grade security vulnerability detection - score STRICTLY between 0 and 1"""
    issue = prediction.get("issue", "").lower() if prediction.get("issue") else ""
    
    score = 0.15
    
    if "sql injection" in issue:
        score = 0.88
    elif "injection" in issue:
        score = 0.75
    elif "sql" in issue or "query" in issue:
        score = 0.65
    elif issue:
        score = 0.45
    else:
        score = 0.25
    
    # CRITICAL: Ensure score is NEVER 0.0 or 1.0
    if score >= 0.99:
        score = 0.98
    if score <= 0.01:
        score = 0.02
    
    return score


# This MUST be named GRADERS and be a dictionary
GRADERS = {
    "easy": grade_easy,
    "medium": grade_medium,
    "hard": grade_hard
}
