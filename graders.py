# graders.py

def easy_grader(prediction):
    """
    Grade syntax error detection
    Score MUST be strictly between 0 and 1 (not 0.0, not 1.0)
    """
    issue = prediction.get("issue", "").lower()
    suggestions = prediction.get("suggestions", [])
    
    # Start with base score > 0
    score = 0.05
    
    # Evaluate issue identification (max 0.70)
    if "missing" in issue and ("parenthesis" in issue or "parentheses" in issue):
        score += 0.65  # Total: 0.70
    elif "syntax" in issue:
        score += 0.55  # Total: 0.60
    elif "print" in issue:
        score += 0.45  # Total: 0.50
    elif "error" in issue:
        score += 0.35  # Total: 0.40
    elif "incomplete" in issue:
        score += 0.25  # Total: 0.30
    else:
        score += 0.15  # Total: 0.20 (partial credit)
    
    # Evaluate suggestions quality (max 0.24)
    if suggestions:
        suggestion_score = 0
        for suggestion in suggestions:
            suggestion_lower = suggestion.lower()
            if "parenthesis" in suggestion_lower or "closing" in suggestion_lower:
                suggestion_score += 0.12
            elif "fix" in suggestion_lower or "correct" in suggestion_lower:
                suggestion_score += 0.08
            elif "syntax" in suggestion_lower:
                suggestion_score += 0.06
        
        score += min(suggestion_score, 0.24)  # Max total: 0.94
    
    # Ensure score is strictly between 0 and 1
    score = max(0.01, min(score, 0.99))
    
    return score


def medium_grader(prediction):
    """
    Grade runtime bug detection
    Score MUST be strictly between 0 and 1 (not 0.0, not 1.0)
    """
    issue = prediction.get("issue", "").lower()
    suggestions = prediction.get("suggestions", [])
    
    # Start with base score > 0
    score = 0.05
    
    # Evaluate issue identification (max 0.70)
    if "index" in issue and ("out of range" in issue or "out of bounds" in issue):
        score += 0.65  # Total: 0.70
    elif "index" in issue and "error" in issue:
        score += 0.55  # Total: 0.60
    elif "out of range" in issue or "out of bounds" in issue:
        score += 0.50  # Total: 0.55
    elif "index" in issue:
        score += 0.40  # Total: 0.45
    elif "range" in issue or "bound" in issue:
        score += 0.35  # Total: 0.40
    elif "array" in issue:
        score += 0.30  # Total: 0.35
    else:
        score += 0.15  # Total: 0.20 (partial credit)
    
    # Evaluate suggestions quality (max 0.24)
    if suggestions:
        suggestion_score = 0
        for suggestion in suggestions:
            suggestion_lower = suggestion.lower()
            if "check length" in suggestion_lower or "verify index" in suggestion_lower:
                suggestion_score += 0.12
            elif "try except" in suggestion_lower or "error handling" in suggestion_lower:
                suggestion_score += 0.10
            elif "len()" in suggestion_lower or "array length" in suggestion_lower:
                suggestion_score += 0.08
            elif "loop" in suggestion_lower:
                suggestion_score += 0.06
        
        score += min(suggestion_score, 0.24)  # Max total: 0.94
    
    # Ensure score is strictly between 0 and 1
    score = max(0.01, min(score, 0.99))
    
    return score


def hard_grader(prediction):
    """
    Grade security vulnerability detection
    Score MUST be strictly between 0 and 1 (not 0.0, not 1.0)
    """
    issue = prediction.get("issue", "").lower()
    suggestions = prediction.get("suggestions", [])
    
    # Start with base score > 0
    score = 0.05
    
    # Evaluate issue identification (max 0.65)
    if "sql injection" in issue:
        score += 0.60  # Total: 0.65
    elif "injection" in issue and "sql" in issue:
        score += 0.55  # Total: 0.60
    elif "injection" in issue:
        score += 0.45  # Total: 0.50
    elif "sql" in issue or "query" in issue:
        score += 0.35  # Total: 0.40
    elif "vulnerability" in issue or "security" in issue:
        score += 0.30  # Total: 0.35
    elif "input" in issue:
        score += 0.25  # Total: 0.30
    else:
        score += 0.15  # Total: 0.20 (partial credit)
    
    # Evaluate security suggestions (max 0.29)
    if suggestions:
        security_score = 0
        for suggestion in suggestions:
            suggestion_lower = suggestion.lower()
            if "parameterized" in suggestion_lower or "prepared statement" in suggestion_lower:
                security_score += 0.15
            elif "sanitize" in suggestion_lower:
                security_score += 0.12
            elif "validate" in suggestion_lower or "validation" in suggestion_lower:
                security_score += 0.10
            elif "escape" in suggestion_lower:
                security_score += 0.08
            elif "best practice" in suggestion_lower:
                security_score += 0.06
        
        score += min(security_score, 0.29)  # Max total: 0.94
    
    # Ensure score is strictly between 0 and 1
    score = max(0.01, min(score, 0.99))
    
    return score


# Dictionary for programmatic access
GRADERS = {
    "easy": easy_grader,
    "medium": medium_grader,
    "hard": hard_grader,
    "easy_grader": easy_grader,
    "medium_grader": medium_grader,
    "hard_grader": hard_grader
}

# List all available grader names for enumeration
ALL_GRADERS = ["easy_grader", "medium_grader", "hard_grader"]
