def grade_easy(prediction):
    """
    Grader for easy difficulty - syntax error detection
    
    Args:
        prediction: dict with 'issue' and 'suggestions' keys
    
    Returns:
        float: Score between 0 and 1
    """
    issue = prediction.get("issue", "").lower()
    suggestions = prediction.get("suggestions", [])
    
    # Exact match for the specific syntax error
    if "missing parenthesis" in issue or "missing parentheses" in issue:
        return 1.0
    # Partial credit for generic syntax error identification
    elif "syntax" in issue:
        return 0.7
    # Minimal credit for any response
    elif len(issue) > 10:
        return 0.3
    else:
        return 0.0


def grade_medium(prediction):
    """
    Grader for medium difficulty - runtime bug detection
    
    Args:
        prediction: dict with 'issue' and 'suggestions' keys
    
    Returns:
        float: Score between 0 and 1
    """
    issue = prediction.get("issue", "").lower()
    suggestions = prediction.get("suggestions", [])
    
    # Exact match for index out of range
    if "index out of range" in issue or "index out of bounds" in issue:
        return 1.0
    # Partial for array/list related issues
    elif "array" in issue or "list" in issue or "index" in issue:
        return 0.6
    # Minimal credit for runtime-related response
    elif "runtime" in issue or "error" in issue:
        return 0.3
    else:
        return 0.0


def grade_hard(prediction):
    """
    Grader for hard difficulty - security vulnerability detection
    
    Args:
        prediction: dict with 'issue' and 'suggestions' keys
    
    Returns:
        float: Score between 0 and 1
    """
    issue = prediction.get("issue", "").lower()
    suggestions = prediction.get("suggestions", [])
    
    base_score = 0.0
    
    # Check issue identification
    if "sql injection" in issue or "sql injection vulnerability" in issue:
        base_score = 0.6
    elif "injection" in issue or "sql" in issue:
        base_score = 0.4
    elif "security" in issue or "vulnerability" in issue:
        base_score = 0.2
    
    # Bonus for good suggestions (up to 0.4 extra)
    suggestion_bonus = 0.0
    security_keywords = [
        "parameterized", "prepared statement", "sanitize", 
        "validate", "escape", "input validation", "orm"
    ]
    
    for suggestion in suggestions:
        suggestion_lower = suggestion.lower()
        for keyword in security_keywords:
            if keyword in suggestion_lower:
                suggestion_bonus += 0.1
                break  # Only count once per suggestion
    
    # Cap at 1.0
    return min(base_score + suggestion_bonus, 1.0)


# IMPORTANT: This dictionary is what the validator looks for
GRADERS = {
    "easy": grade_easy,
    "medium": grade_medium,
    "hard": grade_hard
}
