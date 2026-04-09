def grade_easy(prediction):
    """
    Grade syntax and style review
    Score between 0.01 and 0.99
    """
    issues_found = prediction.get("issues_found", [])
    expected_issues = prediction.get("expected_issues", [
        "missing colon", "syntax error", "indentation"
    ])
    
    score = 0.05  # Base participation score
    
    # Score based on issues correctly identified
    if issues_found:
        correct_finds = 0
        for issue in issues_found:
            issue_text = issue.get("description", "").lower()
            for expected in expected_issues:
                if expected in issue_text:
                    correct_finds += 0.35
                    break
        
        score += min(correct_finds, 0.70)
    
    # Bonus for suggesting fixes
    suggestions = prediction.get("suggestions", [])
    if suggestions:
        suggestion_bonus = min(len(suggestions) * 0.08, 0.20)
        score += suggestion_bonus
    
    return min(max(score, 0.01), 0.99)


def grade_medium(prediction):
    """
    Grade logic and performance review
    Score between 0.01 and 0.99
    """
    issues_found = prediction.get("issues_found", [])
    expected_issues = prediction.get("expected_issues", [
        "off by one", "index error", "infinite loop", 
        "boundary condition", "null check"
    ])
    
    score = 0.05  # Base participation score
    
    # Score based on logic issues identified
    if issues_found:
        correct_finds = 0
        for issue in issues_found:
            issue_text = issue.get("description", "").lower()
            for expected in expected_issues:
                if expected in issue_text:
                    correct_finds += 0.30
                    break
            # Partial credit for being close
            elif "logic" in issue_text or "bug" in issue_text:
                correct_finds += 0.15
        
        score += min(correct_finds, 0.65)
    
    # Bonus for fix suggestions and edge cases
    suggestions = prediction.get("suggestions", [])
    if suggestions:
        quality_bonus = 0
        for suggestion in suggestions:
            text = suggestion.get("text", "").lower()
            if "fix" in text or "solution" in text:
                quality_bonus += 0.06
            if "edge case" in text or "boundary" in text:
                quality_bonus += 0.08
        
        score += min(quality_bonus, 0.25)
    
    return min(max(score, 0.01), 0.99)


def grade_hard(prediction):
    """
    Grade security and architecture review
    Score between 0.01 and 0.99
    """
    issues_found = prediction.get("issues_found", [])
    expected_issues = prediction.get("expected_issues", [
        "sql injection", "xss", "authentication", 
        "authorization", "input validation", "secure"
    ])
    
    score = 0.05  # Base participation score
    
    # Higher weight for security issues
    if issues_found:
        security_score = 0
        for issue in issues_found:
            issue_text = issue.get("description", "").lower()
            severity = issue.get("severity", "warning").lower()
            
            # Security issues are critical
            if severity == "critical":
                security_score += 0.45
            elif severity == "error":
                security_score += 0.35
            
            # Check for expected security terms
            for expected in expected_issues:
                if expected in issue_text:
                    security_score += 0.10
                    break
        
        score += min(security_score, 0.70)
    
    # Bonus for security best practices
    suggestions = prediction.get("suggestions", [])
    if suggestions:
        security_bonus = 0
        security_terms = ["parameterized", "prepared statement", "escape", 
                         "sanitize", "validate", "authentication", "encrypt"]
        
        for suggestion in suggestions:
            text = suggestion.get("text", "").lower()
            for term in security_terms:
                if term in text:
                    security_bonus += 0.10
                    break
        
        score += min(security_bonus, 0.20)
    
    return min(max(score, 0.01), 0.99)


GRADERS = {
    "easy": grade_easy,
    "medium": grade_medium,
    "hard": grade_hard
}
