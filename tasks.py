TASKS = {
    "easy": {
        "id": "easy_001",
        "difficulty": "easy",
        "grader": True,
        "reward_range": (0.01, 0.99),
        "code": "print('Hello World'",
        "issue": "missing_parenthesis"
    },

    "medium": {
        "id": "medium_001",
        "difficulty": "medium",
        "grader": True,
        "reward_range": (0.01, 0.99),
        "code": """
arr = [1, 2, 3]
for i in range(5):
    print(arr[i])
""",
        "issue": "index_out_of_range"
    },

    "hard": {
        "id": "hard_001",
        "difficulty": "hard",
        "grader": True,
        "reward_range": (0.01, 0.99),
        "code": """
query = "SELECT * FROM users WHERE id=" + user_input
""",
        "issue": "sql_injection"
    }
}
