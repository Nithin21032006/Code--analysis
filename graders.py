# env/graders.py
def grade_easy(prediction):
    """Grade syntax error detection - score between 0.10 and 0.99"""
    issue = prediction.get("issue", "").lower() if prediction.get("issue") else ""
    
    if "missing" in issue and ("parenthesis" in issue or "colon" in issue):
        return 0.85
    elif "syntax" in issue:
        return 0.75
    elif "error" in issue:
        return 0.65
    else:
        return 0.45


def grade_medium(prediction):
    """Grade runtime bug detection - score between 0.10 and 0.99"""
    issue = prediction.get("issue", "").lower() if prediction.get("issue") else ""
    
    if "index" in issue and ("out of range" in issue or "out of bounds" in issue):
        return 0.85
    elif "index" in issue:
        return 0.70
    elif "range" in issue or "bound" in issue:
        return 0.60
    else:
        return 0.45


def grade_hard(prediction):
    """Grade security vulnerability detection - score between 0.10 and 0.99"""
    issue = prediction.get("issue", "").lower() if prediction.get("issue") else ""
    
    if "sql injection" in issue:
        return 0.88
    elif "injection" in issue:
        return 0.75
    elif "sql" in issue or "query" in issue:
        return 0.65
    else:
        return 0.45


GRADERS = {
    "grade_easy": grade_easy,
    "grade_medium": grade_medium,
    "grade_hard": grade_hard
}