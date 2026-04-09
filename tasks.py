TASKS = [
    {
        "id": "easy",
        "name": "Syntax Error Detection",
        "difficulty": "easy",
        "objective": "Identify and fix syntax errors in Python code, specifically missing parentheses in print statements.",
        "grader": "easy",
        "sample_code": "print('Hello World'"
    },
    {
        "id": "medium",
        "name": "Runtime Bug Detection",
        "difficulty": "medium",
        "objective": "Detect runtime bugs like index out of range errors in loops.",
        "grader": "medium",
        "sample_code": "arr = [1, 2, 3]\nfor i in range(5):\n    print(arr[i])"
    },
    {
        "id": "hard",
        "name": "Security Vulnerability Detection",
        "difficulty": "hard",
        "objective": "Identify security vulnerabilities like SQL injection in database queries.",
        "grader": "hard",
        "sample_code": 'query = "SELECT * FROM users WHERE id=" + user_input'
    }
]
