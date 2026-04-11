def grade_easy(prediction):
    """Syntax error grader"""
    return 0.75

def grade_medium(prediction):
    """Runtime bug grader"""
    return 0.65

def grade_hard(prediction):
    """Security vulnerability grader"""
    return 0.85

GRADERS = {
    "easy": grade_easy,
    "medium": grade_medium,
    "hard": grade_hard
}
