def grade_easy(action):
    issue = action.get("payload", {}).get("issue", "")
    if issue == "missing_parenthesis":
        return 0.8, True, "Correct syntax issue detected"
    return 0.2, False, "Wrong syntax issue"


def grade_medium(action):
    issue = action.get("payload", {}).get("issue", "")
    if issue == "index_out_of_range":
        return 0.8, True, "Correct runtime issue detected"
    return 0.2, False, "Wrong runtime issue"


def grade_hard(action):
    issue = action.get("payload", {}).get("issue", "")
    if issue == "sql_injection":
        return 0.8, True, "Correct security issue detected"
    return 0.2, False, "Wrong security issue"


def grade_action(task, action):
    difficulty = task["difficulty"]

    if difficulty == "easy":
        return grade_easy(action)

    elif difficulty == "medium":
        return grade_medium(action)

    elif difficulty == "hard":
        return grade_hard(action)

    return 0.1, False, "Unknown task"
