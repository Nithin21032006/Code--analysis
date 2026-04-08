TASKS = {
    "easy": {
        "id": "easy",
        "difficulty": "easy",
        "grader": "grade_easy",
        "code": "print('Hello World'",
        "issue": "missing_parenthesis"
    },

    "medium": {
        "id": "medium",
        "difficulty": "medium",
        "grader": "grade_medium",
        "code": """
arr = [1, 2, 3]
for i in range(5):
    print(arr[i])
""",
        "issue": "index_out_of_range"
    },

    "hard": {
        "id": "hard",
        "difficulty": "hard",
        "grader": "grade_hard",
        "code": """
query = "SELECT * FROM users WHERE id=" + user_input
""",
        "issue": "sql_injection"
    }
}
