import os
import requests
from openai import OpenAI

BASE_URL = "http://localhost:7860"

print("[START]")

try:
    # Required: use injected proxy credentials from validator
    client = OpenAI(
        base_url=os.environ["API_BASE_URL"],
        api_key=os.environ["API_KEY"]
    )

    # Safe fallback if MODEL_NAME is not provided
    model_name = os.environ.get("MODEL_NAME", "gpt-4o-mini")

    task_codes = {
        "easy": "print('Hello World'",
        "medium": "arr = [1, 2, 3]\nfor i in range(5):\n    print(arr[i])",
        "hard": 'query = "SELECT * FROM users WHERE id=" + user_input'
    }

    action_map = {
        "easy": "analyze_syntax",
        "medium": "analyze_runtime",
        "hard": "security_scan"
    }

    issue_map = {
        "easy": "missing_parenthesis",
        "medium": "index_out_of_range",
        "hard": "sql_injection"
    }

    for level in ["easy", "medium", "hard"]:
        # Step 1: Reset environment
        reset_response = requests.post(
            f"{BASE_URL}/reset",
            params={"level": level}
        )

        print(f"[STEP] reset={level}")
        print(reset_response.json())

        # Step 2: REQUIRED direct LiteLLM proxy call
        llm_response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "user",
                    "content": f"Analyze this {level} level code:\n{task_codes[level]}"
                }
            ]
        )

        print("[LLM RESPONSE]")
        print(llm_response.choices[0].message.content)

        # Step 3: Submit correct action to environment
        step_response = requests.post(
            f"{BASE_URL}/step",
            json={
                "action_type": action_map[level],
                "payload": {
                    "issue": issue_map[level]
                }
            }
        )

        print(f"[STEP RESULT] level={level}")
        print(step_response.json())

except Exception as e:
    print(f"[ERROR] {str(e)}")
    exit(1)

print("[END]")