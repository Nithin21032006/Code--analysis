# tasks.py
TASKS = [
    {
        "id": "easy",
        "name": "Syntax & Style Review",
        "difficulty": "easy",
        "objective": "Identify syntax errors, missing imports, and style violations",
        "grader_name": "grade_easy",
        "sample_pr": {
            "title": "Fix calculator implementation",
            "description": "Added new calculator functions",
            "files": [
                {
                    "filename": "calculator.py",
                    "content": "def add(a,b)\n    return a+b\n\ndef subtract(a,b):\n    return a-b",
                    "issues": [
                        {"line": 1, "type": "syntax", "description": "Missing colon after function definition"},
                        {"line": 2, "type": "syntax", "description": "Indentation error"}
                    ]
                }
            ]
        }
    },
    {
        "id": "medium",
        "name": "Logic & Performance Review",
        "difficulty": "medium",
        "objective": "Find logic bugs and off-by-one errors",
        "grader_name": "grade_medium",
        "sample_pr": {
            "title": "Implement binary search",
            "description": "Added binary search algorithm",
            "files": [
                {
                    "filename": "search.py",
                    "content": "def binary_search(arr, target):\n    left = 0\n    right = len(arr)\n    while left < right:\n        mid = (left + right) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            right = mid\n        else:\n            left = mid + 1\n    return -1",
                    "issues": [
                        {"line": 2, "type": "logic", "description": "Should be len(arr) - 1"},
                        {"line": 7, "type": "logic", "description": "Wrong direction - should update left"}
                    ]
                }
            ]
        }
    },
    {
        "id": "hard",
        "name": "Security & Architecture Review",
        "difficulty": "hard",
        "objective": "Detect SQL injection and security vulnerabilities",
        "grader_name": "grade_hard",
        "sample_pr": {
            "title": "Add user authentication",
            "description": "Implemented login endpoint",
            "files": [
                {
                    "filename": "auth.py",
                    "content": "def login(username, password):\n    query = f\"SELECT * FROM users WHERE username='{username}' AND password='{password}'\"\n    return db.execute(query)",
                    "issues": [
                        {"line": 1, "type": "security", "severity": "critical", "description": "SQL injection vulnerability"},
                        {"line": 1, "type": "security", "severity": "critical", "description": "Plain text password storage"}
                    ]
                }
            ]
        }
    }
]

def get_task(task_id):
    for task in TASKS:
        if task["id"] == task_id:
            return task
    return None
