TASKS = [
    {
        "id": "easy",
        "name": "Syntax Error Detection",
        "difficulty": "easy",
        "objective": "Identify missing parentheses and syntax errors",
        "grader": "easy",  # Must match key in GRADERS
        "sample_code": "def add(a,b)\n    return a+b"
    },
    {
        "id": "medium",
        "name": "Runtime Bug Detection",
        "difficulty": "medium",
        "objective": "Detect index out of range errors",
        "grader": "medium",  # Must match key in GRADERS
        "sample_code": "arr = [1,2,3]\nfor i in range(5):\n    print(arr[i])"
    },
    {
        "id": "hard",
        "name": "Security Vulnerability Detection",
        "difficulty": "hard",
        "objective": "Identify SQL injection vulnerabilities",
        "grader": "hard",  # Must match key in GRADERS
        "sample_code": 'query = "SELECT * FROM users WHERE id=" + user_input'
    }
]

def get_task(task_id):
    for task in TASKS:
        if task["id"] == task_id:
            return task
    return None
