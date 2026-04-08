# tasks.py

TASKS = [
    {
        "id": "easy",
        "difficulty": "easy",
        "objective": "Detect syntax errors",
        "grader": "grade_easy",
        "expected_issue": "missing_parenthesis"
    },
    {
        "id": "medium",
        "difficulty": "medium",
        "objective": "Detect runtime errors",
        "grader": "grade_medium",
        "expected_issue": "index_out_of_range"
    },
    {
        "id": "hard",
        "difficulty": "hard",
        "objective": "Detect security vulnerabilities",
        "grader": "grade_hard",
        "expected_issue": "sql_injection"
    }
]
