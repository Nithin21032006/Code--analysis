TASKS = [
    {
        "id": "easy",
        "name": "Syntax & Style Review",
        "difficulty": "easy",
        "objective": "Identify syntax errors, missing imports, and style violations (PEP 8)",
        "grader": "grade_easy",
        "sample_pr": {
            "title": "Fix calculator implementation",
            "description": "Added new calculator functions",
            "files": [
                {
                    "filename": "calculator.py",
                    "content": "def add(a,b)\n    return a+b\n\ndef subtract(a,b):\n    return a-b\n\ndef multiply(a,b)\n    return a*b",
                    "issues": [
                        {"line": 1, "type": "syntax", "description": "Missing colon after function definition"},
                        {"line": 5, "type": "syntax", "description": "Missing colon after function definition"}
                    ]
                }
            ]
        }
    },
    {
        "id": "medium",
        "name": "Logic & Performance Review",
        "difficulty": "medium",
        "objective": "Find logic bugs, off-by-one errors, inefficient algorithms, and edge cases",
        "grader": "grade_medium",
        "sample_pr": {
            "title": "Optimize search algorithm",
            "description": "Implemented binary search",
            "files": [
                {
                    "filename": "search.py",
                    "content": "def binary_search(arr, target):\n    left = 0\n    right = len(arr)\n    while left < right:\n        mid = (left + right) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            right = mid\n        else:\n            left = mid + 1\n    return -1",
                    "issues": [
                        {"line": 2, "type": "logic", "description": "Should be len(arr) - 1 for right bound"},
                        {"line": 7, "type": "logic", "description": "Wrong direction - should update left = mid + 1"},
                        {"line": 8, "type": "logic", "description": "Wrong direction - should update right = mid"}
                    ]
                }
            ]
        }
    },
    {
        "id": "hard",
        "name": "Security & Architecture Review",
        "difficulty": "hard",
        "objective": "Detect SQL injection, XSS vulnerabilities, authentication flaws, and architectural issues",
        "grader": "grade_hard",
        "sample_pr": {
            "title": "Add user authentication",
            "description": "Implemented login endpoint",
            "files": [
                {
                    "filename": "auth.py",
                    "content": "def login(username, password):\n    query = f\"SELECT * FROM users WHERE username='{username}' AND password='{password}'\"\n    result = db.execute(query)\n    return result is not None\n\ndef get_user_data(user_id):\n    data = cache.get(user_id)\n    if not data:\n        data = db.query(f\"SELECT * FROM user_data WHERE id={user_id}\")\n    return data",
                    "issues": [
                        {"line": 2, "type": "security", "description": "SQL injection vulnerability - using string formatting"},
                        {"line": 8, "type": "security", "description": "SQL injection in second query"},
                        {"line": 1, "type": "security", "description": "No password hashing - storing plain text"}
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
