def grade_easy(prediction):
    """Grade syntax error detection - score between 0.01 and 0.99"""
    issue = prediction.get("issue", "").lower()
    
    score = 0.05
    
    if "missing" in issue and ("parenthesis" in issue or "colon" in issue):
        score += 0.70
    elif "syntax" in issue:
        score += 0.55
    elif "error" in issue:
        score += 0.40
    else:
        score += 0.20
    
    return min(max(score, 0.01), 0.99)


def grade_medium(prediction):
    """Grade runtime bug detection - score between 0.01 and 0.99"""
    issue = prediction.get("issue", "").lower()
    
    score = 0.05
    
    if "index" in issue and ("out of range" in issue or "out of bounds" in issue):
        score += 0.65
    elif "index" in issue:
        score += 0.50
    elif "range" in issue or "bound" in issue:
        score += 0.40
    else:
        score += 0.25
    
    return min(max(score, 0.01), 0.99)


def grade_hard(prediction):
    """Grade security vulnerability detection - score between 0.01 and 0.99"""
    issue = prediction.get("issue", "").lower()
    
    score = 0.05
    
    if "sql injection" in issue:
        score += 0.65
    elif "injection" in issue:
        score += 0.50
    elif "sql" in issue or "query" in issue:
        score += 0.40
    else:
        score += 0.25
    
    return min(max(score, 0.01), 0.99)


# GRADERS dictionary - keys must match the "grader" field in tasks.py
GRADERS = {
    "easy": grade_easy,
    "medium": grade_medium,
    "hard": grade_hard
}
