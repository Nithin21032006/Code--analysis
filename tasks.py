TASKS = [
    {
        "id": "easy",
        "name": "Syntax Error Detection",
        "difficulty": "easy",
        "objective": "Identify syntax errors like missing parentheses, brackets, or quotes",
        "grader": "grade_easy"  # Must match function name in graders.py
    },
    {
        "id": "medium",
        "name": "Runtime Bug Detection",
        "difficulty": "medium",
        "objective": "Detect index out of range, null pointer, or other runtime errors",
        "grader": "grade_medium"
    },
    {
        "id": "hard",
        "name": "Security Vulnerability Detection",
        "difficulty": "hard",
        "objective": "Find SQL injection, XSS, or other security vulnerabilities",
        "grader": "grade_hard"
    }
]
