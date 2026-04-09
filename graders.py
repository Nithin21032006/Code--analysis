def grade_easy(prediction):
    """
    Grade syntax error detection
    Score must be strictly between 0 and 1 (not 0.0, not 1.0)
    """
    expected_issues = ["missing parenthesis", "syntax error", "print statement"]
    issue = prediction.get("issue", "").lower()
    suggestions = prediction.get("suggestions", [])
    
    # Start with a base score
    score = 0.01  # Minimum score > 0
    
    # Check if issue is correctly identified
    for expected in expected_issues:
        if expected in issue:
            score += 0.6  # Brings to 0.61 (valid range)
            break
    
    # Add points for good suggestions
    if suggestions and len(suggestions) > 0:
        score += 0.2  # Brings to 0.81 max
    
    # Add small bonus for specific keywords
    if "parenthesis" in issue or "parentheses" in issue:
        score += 0.1  # Brings to 0.91 max
    
    # Ensure score is strictly between 0 and 1
    score = min(max(score, 0.01), 0.99)
    
    return score


def grade_medium(prediction):
    """
    Grade runtime bug detection
    Score must be strictly between 0 and 1 (not 0.0, not 1.0)
    """
    expected_issues = ["index out of range", "out of bounds", "array index", "index error"]
    issue = prediction.get("issue", "").lower()
    suggestions = prediction.get("suggestions", [])
    
    # Start with a base score
    score = 0.01  # Minimum score > 0
    
    # Check if issue is correctly identified
    issue_score = 0
    for expected in expected_issues:
        if expected in issue:
            issue_score = 0.55
            break
        elif "index" in issue and ("range" in issue or "bound" in issue):
            issue_score = 0.45
    
    score += issue_score
    
    # Add points for quality suggestions
    suggestion_bonus = 0
    for suggestion in suggestions:
        if "check" in suggestion.lower() or "verify" in suggestion.lower():
            suggestion_bonus += 0.1
        if "try" in suggestion.lower() or "except" in suggestion.lower():
            suggestion_bonus += 0.1
        if "len" in suggestion.lower() or "length" in suggestion.lower():
            suggestion_bonus += 0.1
    
    score += min(suggestion_bonus, 0.35)  # Cap at 0.35
    
    # Ensure score is strictly between 0 and 1
    score = min(max(score, 0.01), 0.99)
    
    return score


def grade_hard(prediction):
    """
    Grade security vulnerability detection
    Score must be strictly between 0 and 1 (not 0.0, not 1.0)
    """
    expected_issues = ["sql injection", "injection vulnerability", "sql injection vulnerability"]
    issue = prediction.get("issue", "").lower()
    suggestions = prediction.get("suggestions", [])
    
    # Start with a base score
    score = 0.01  # Minimum score > 0
    
    # Check if issue is correctly identified
    issue_score = 0
    for expected in expected_issues:
        if expected in issue:
            issue_score = 0.5
            break
        elif "injection" in issue:
            issue_score = 0.4
        elif "sql" in issue or "query" in issue:
            issue_score = 0.3
    
    score += issue_score
    
    # Check suggestions for security best practices
    security_keywords = {
        "parameterized": 0.15,
        "prepared statement": 0.15,
        "sanitize": 0.12,
        "validation": 0.12,
        "escape": 0.10,
        "input validation": 0.10,
        "orm": 0.08,
        "bind variable": 0.08
    }
    
    suggestion_score = 0
    for suggestion in suggestions:
        suggestion_lower = suggestion.lower()
        for keyword, points in security_keywords.items():
            if keyword in suggestion_lower:
                suggestion_score += points
                break  # Only count highest match per suggestion
    
    score += min(suggestion_score, 0.4)  # Cap at 0.4
    
    # Ensure score is strictly between 0 and 1
    score = min(max(score, 0.01), 0.99)
    
    return score


# Graders dictionary - MUST have at least 3 tasks
GRADERS = {
    "easy": grade_easy,
    "medium": grade_medium,
    "hard": grade_hard
}
