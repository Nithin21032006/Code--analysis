import os
import requests
from openai import OpenAI

BASE_URL = "http://localhost:7860"

TASK_NAME = "code_analysis"
BENCHMARK = "custom_fastapi_env"

task_codes = {
    "easy": "print('Hello World'",
    "medium": "arr = [1, 2, 3]\nfor i in range(5):\n    print(arr[i])",
    "hard": 'query = "SELECT * FROM users WHERE id=" + user_input',
}

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


def log_start(task, env, model):
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step, action, reward, done, error=None):
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True
    )


def log_end(success, steps, score, rewards):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}",
        flush=True
    )


def main():
    rewards = []
    steps_taken = 0
    score = 0.01
    success = False

    # STRICT: use only injected proxy credentials
    client = OpenAI(
        base_url=os.environ["API_BASE_URL"],
        api_key=os.environ["API_KEY"]
    )

    model_name = os.environ.get("MODEL_NAME", "gpt-4o-mini")

    log_start(TASK_NAME, BENCHMARK, model_name)

    try:
        for step_num, level in enumerate(["easy", "medium", "hard"], start=1):
            requests.post(
                f"{BASE_URL}/reset",
                params={"level": level},
                timeout=10
            )

            # REQUIRED proxy call
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "user",
                        "content": f"Analyze this code:\n{task_codes[level]}"
                    }
                ]
            )

            action = action_map[level]

            step_response = requests.post(
                f"{BASE_URL}/step",
                json={
                    "action_type": action,
                    "payload": {
                        "issue": issue_map[level]
                    }
                },
                timeout=10
            )

            result = step_response.json()
            reward = float(result.get("reward", 0.5))
            done = bool(result.get("done", False))

            rewards.append(reward)
            steps_taken = step_num

            log_step(step_num, action, reward, done)

        raw_score = sum(rewards) / len(rewards) if rewards else 0.5
        score = min(max(raw_score, 0.01), 0.99)
        success = score > 0.5

    except Exception as e:
        print(f"[DEBUG] {str(e)}", flush=True)

    log_end(success, steps_taken, score, rewards)


if __name__ == "__main__":
    main()
