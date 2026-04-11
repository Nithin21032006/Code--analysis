TASKS = [
    {
        "id": "easy",
        "name": "Syntax Error Detection",
        "difficulty": "easy",
        "objective": "Identify missing parentheses and syntax errors",
        "grader": "easy"  # Must match key in GRADERS
    },
    {
        "id": "medium",
        "name": "Runtime Bug Detection",
        "difficulty": "medium",
        "objective": "Detect index out of range errors",
        "grader": "medium"  # Must match key in GRADERS
    },
    {
        "id": "hard",
        "name": "Security Vulnerability Detection",
        "difficulty": "hard",
        "objective": "Identify SQL injection vulnerabilities",
        "grader": "hard"  # Must match key in GRADERS
    }
]

# Also export as OPENENV_TASKS
OPENENV_TASKS = TASKS
