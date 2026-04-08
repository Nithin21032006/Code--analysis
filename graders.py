# graders.py

def grade_easy(prediction: dict) -> float:
    """
    Easy task: syntax error detection
    """
    issue = prediction.get("issue", "")

    if issue == "missing_parenthesis":
        return 0.8

    return 0.2


def grade_medium(prediction: dict) -> float:
    """
    Medium task: runtime bug detection
    """
    issue = prediction.get("issue", "")

    if issue == "index_out_of_range":
        return 0.8

    return 0.2


def grade_hard(prediction: dict) -> float:
    """
    Hard task: security vulnerability detection
    """
    issue = prediction.get("issue", "")

    if issue == "sql_injection":
        return 0.8

    return 0.2


# validator-friendly mapping
GRADERS = {
    "easy": grade_easy,
    "medium": grade_medium,
    "hard": grade_hard
}
