def grade_easy(prediction):
    """Grade syntax error detection - score between 0.10 and 0.99"""
    issue = prediction.get("issue", "").lower() if prediction.get("issue") else ""
    
    score = 0.10  # Minimum base score
    
    if "missing" in issue and ("parenthesis" in issue or "colon" in issue):
        score = 0.85
    elif "syntax" in issue:
        score = 0.75
    elif "error" in issue:
        score = 0.65
    elif "print" in issue:
        score = 0.55
    elif issue:
        score = 0.40
    else:
        score = 0.20
    
    # Cap at 0.99 maximum
    if score > 0.99:
        score = 0.99
    if score < 0.10:
        score = 0.10
    
    return score


def grade_medium(prediction):
    """Grade runtime bug detection - score between 0.10 and 0.99"""
    issue = prediction.get("issue", "").lower() if prediction.get("issue") else ""
    
    score = 0.10  # Minimum base score
    
    if "index" in issue and ("out of range" in issue or "out of bounds" in issue):
        score = 0.85
    elif "index" in issue:
        score = 0.75
    elif "range" in issue or "bound" in issue:
        score = 0.65
    elif "array" in issue:
        score = 0.55
    elif issue:
        score = 0.40
    else:
        score = 0.20
    
    # Cap at 0.99 maximum
    if score > 0.99:
        score = 0.99
    if score < 0.10:
        score = 0.10
    
    return score


def grade_hard(prediction):
    """Grade security vulnerability detection - score between 0.10 and 0.99"""
    issue = prediction.get("issue", "").lower() if prediction.get("issue") else ""
    
    score = 0.10  # Minimum base score
    
    if "sql injection" in issue:
        score = 0.88
    elif "injection" in issue:
        score = 0.78
    elif "sql" in issue or "query" in issue:
        score = 0.68
    elif "vulnerability" in issue:
        score = 0.58
    elif "security" in issue:
        score = 0.48
    elif issue:
        score = 0.38
    else:
        score = 0.20
    
    # Cap at 0.99 maximum
    if score > 0.99:
        score = 0.99
    if score < 0.10:
        score = 0.10
    
    return score


# GRADERS dictionary
GRADERS = {
    "easy": grade_easy,
    "medium": grade_medium,
    "hard": grade_hard
}
