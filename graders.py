def grade_action(task, action):
    expected_issue = task["issue"]
    detected_issue = action.payload.get("issue", "").lower() if action.payload else ""
    action_type = action.action_type.lower() if hasattr(action, "action_type") else ""

    # EASY
    if task["difficulty"] == "easy":
        if action_type == "analyze_syntax":
            return 0.5, False, "Syntax analysis started"
        if detected_issue == expected_issue:
            return 1.0, True, "Correct syntax issue detected"

    # MEDIUM
    elif task["difficulty"] == "medium":
        if action_type == "analyze_runtime":
            return 0.4, False, "Potential runtime issue found"
        if detected_issue == expected_issue:
            return 1.0, True, "Runtime bug correctly detected"

    # HARD
    elif task["difficulty"] == "hard":
        if action_type == "security_scan":
            return 0.4, False, "Security scan completed"
        if detected_issue == expected_issue:
            return 1.0, True, "Critical security issue detected"

    return 0.0, False, "Incorrect analysis"