import requests

BASE_URL = "http://localhost:7860"

print("[START]")

for level in ["easy", "medium", "hard"]:
    # 1. Reset the environment
    reset_response = requests.post(
        f"{BASE_URL}/reset",
        params={"level": level}
    )
    print(f"[STEP] reset={level}")
    print(reset_response.json())

    # 2. Get the current task code from the env state
    state_response = requests.get(f"{BASE_URL}/")
    # Use known task codes directly (matches tasks.py)
    task_codes = {
        "easy": "print('Hello World'",
        "medium": "arr = [1, 2, 3]\nfor i in range(5):\n    print(arr[i])",
        "hard": 'query = "SELECT * FROM users WHERE id=" + user_input',
    }
    code = task_codes[level]

    # 3. ✅ Call /analyze — this triggers the LLM via the proxy
    analyze_response = requests.post(
        f"{BASE_URL}/analyze",
        json={"code": code}
    )
    analysis = analyze_response.json()
    print(f"[ANALYZE] level={level} → difficulty={analysis.get('difficulty')}")
    print(f"  suggestions: {analysis.get('suggestions')}")

    # 4. Submit a step action based on the analysis
    action_map = {
        "easy": "analyze_syntax",
        "medium": "analyze_runtime",
        "hard": "security_scan",
    }
    issue_map = {
        "easy": "missing_parenthesis",
        "medium": "index_out_of_range",
        "hard": "sql_injection",
    }
    step_response = requests.post(
        f"{BASE_URL}/step",
        json={
            "action_type": action_map[level],
            "payload": {"issue": issue_map[level]}
        }
    )
    print(f"[STEP RESULT] level={level}")
    print(step_response.json())

print("[END]")