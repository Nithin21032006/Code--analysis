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
        "difficulty":# tasks.py
TASKS = [
    {
        "id": "easy",
        "name": "Syntax Error Detection",
        "difficulty": "easy",
        "objective": "Identify missing parentheses in print statements",
        "grader_name": "easy_grader",
        "sample_code": "print('Hello World'"
    },
    {
        "id": "medium",
        "name": "Runtime Bug Detection",
        "difficulty": "medium",
        "objective": "Detect index out of range errors in loops",
        "grader_name": "medium_grader",
        "sample_code": "arr = [1, 2, 3]\nfor i in range(5):\n    print(arr[i])"
    },
    {
        "id": "hard",
        "name": "Security Vulnerability Detection",
        "difficulty": "hard",
        "objective": "Identify SQL injection vulnerabilities",
        "grader_name": "hard_grader",
        "sample_code": 'query = "SELECT * FROM users WHERE id=" + user_input'
    }
]

def get_all_tasks():
    """Return all tasks for enumeration"""
    return TASKS

def get_task(task_id):
    """Get a specific task by ID"""
    for task in TASKS:
        if task["id"] == task_id:
            return task
    return None "medium",
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
