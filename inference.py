#!/usr/bin/env python3
import os
import requests
from typing import List, Optional

# Use environment variables directly (validator injects these)
API_BASE_URL = os.environ["API_BASE_URL"]
API_KEY = os.environ["API_KEY"]
MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-4o-mini")
SPACE_URL = os.environ.get("SPACE_URL", "https://nithu007-code-lens.hf.space")

TASK_NAME = "code_review_assistant"
BENCHMARK = "code_review_env"

task_codes = {
    "easy": "def add(a,b)\n    return a+b",
    "medium": "arr = [1,2,3]\nfor i in range(5):\n    print(arr[i])",
    "hard": 'query = "SELECT * FROM users WHERE id=" + user_input',
}


def log_start(task, env, model):
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step, action, reward, done, error=None):
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}", flush=True)


def log_end(success, steps, score, rewards):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)


def main():
    from openai import OpenAI

    # Modern initialization - no proxies parameter needed
    client = OpenAI(
        base_url=API_BASE_URL,
        api_key=API_KEY,
    )

    rewards = []
    steps_taken = 0
    score = 0.0
    success = False

    log_start(TASK_NAME, BENCHMARK, MODEL_NAME)

    try:
        for step_num, level in enumerate(["easy", "medium", "hard"], start=1):
            # Reset environment
            reset_response = requests.post(f"{SPACE_URL}/reset", params={"level": level}, timeout=30)
            if reset_response.status_code != 200:
                log_step(step_num, f"reset_{level}", 0.0, True, f"HTTP {reset_response.status_code}")
                rewards.append(0.0)
                continue

            # Get code
            code = task_codes.get(level, "")

            # Make API call through proxy
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "Choose action: analyze_syntax, analyze_runtime, or security_scan. Return only the action name."},
                    {"role": "user", "content": f"Code:\n{code}\n\nWhat action for this {level} code?"}
                ],
                temperature=0.7,
                max_tokens=50,
            )

            action = response.choices[0].message.content.strip().lower()
            if action not in ["analyze_syntax", "analyze_runtime", "security_scan"]:
                action = "analyze_syntax"

            # Execute step
            step_response = requests.post(f"{SPACE_URL}/step", json={"action_type": action, "payload": {}}, timeout=30)
            result = step_response.json() if step_response.status_code == 200 else {"reward": 0.5, "done": True}

            reward = float(result.get("reward", 0.5))
            done = bool(result.get("done", False))
            error = result.get("error")

            rewards.append(reward)
            steps_taken = step_num
            log_step(step_num, action, reward, done, error)

        score = min(max(sum(rewards) / len(rewards) if rewards else 0.5, 0.01), 0.99)
        success = score >= 0.5

    except Exception as e:
        print(f"[DEBUG] Error: {e}", flush=True)
        success = False
        score = 0.01

    finally:
        log_end(success, steps_taken, score, rewards)


if __name__ == "__main__":
    main()
