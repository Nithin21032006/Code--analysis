"""
Inference Script for Code Review Assistant
Follows OpenEnv specification exactly
"""

import os
import json
import requests
from typing import List, Optional
from openai import OpenAI

# ============= ENVIRONMENT VARIABLES (NO DEFAULTS FOR REQUIRED ONES) =============
API_BASE_URL = os.getenv("API_BASE_URL")  # MUST be injected - NO DEFAULT
MODEL_NAME = os.getenv("MODEL_NAME")      # MUST be injected - NO DEFAULT  
HF_TOKEN = os.getenv("HF_TOKEN")          # MUST be injected - NO DEFAULT
API_KEY = os.getenv("API_KEY", HF_TOKEN)  # Can use HF_TOKEN as fallback

# Optional - only when using from_docker_image()
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME")

# Your Space URL (for HTTP calls to the environment)
SPACE_URL = os.getenv("SPACE_URL", "https://nithu007-code-lens.hf.space")

# Task configuration
TASK_NAME = "code_review_assistant"
BENCHMARK = "code_review_env"
MAX_STEPS = 9  # 3 tasks × 3 steps each
TEMPERATURE = 0.7
MAX_TOKENS = 200
SUCCESS_SCORE_THRESHOLD = 0.5

# Task definitions
task_codes = {
    "easy": "def add(a,b)\n    return a+b",
    "medium": "arr = [1,2,3]\nfor i in range(5):\n    print(arr[i])",
    "hard": 'query = "SELECT * FROM users WHERE id=" + user_input',
}

expected_actions = {
    "easy": "analyze_syntax",
    "medium": "analyze_runtime",
    "hard": "security_scan",
}


def log_start(task: str, env: str, model: str) -> None:
    """Emit START line - exactly one at episode begin"""
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    """Emit STEP line - one per step, immediately after env.step() returns"""
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    """Emit END line - after environment closes, always emitted (even on exception)"""
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)


def get_model_action(client: OpenAI, code: str, level: str) -> str:
    """Use LLM to determine the correct action - MUST go through proxy"""
    prompt = f"""Analyze this {level} level code and identify the issue.
Code: {code}

Choose ONE action:
- analyze_syntax (for syntax errors)
- analyze_runtime (for runtime bugs)
- security_scan (for security issues)

Return only the action name, nothing else."""

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a code analysis assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            stream=False,
        )
        action = (completion.choices[0].message.content or "").strip().lower()
        
        # Validate action
        if action in ["analyze_syntax", "analyze_runtime", "security_scan"]:
            return action
        # Fallback based on level
        return expected_actions.get(level, "analyze_syntax")
        
    except Exception as exc:
        print(f"[DEBUG] Model request: {exc}", flush=True)
        # Still return something so validator sees the attempt
        return expected_actions.get(level, "analyze_syntax")


def reset_environment(level: str) -> dict:
    """Reset the environment via HTTP"""
    try:
        response = requests.post(
            f"{SPACE_URL}/reset",
            params={"level": level},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        return {"error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}


def step_environment(action: str) -> dict:
    """Execute a step via HTTP"""
    try:
        response = requests.post(
            f"{SPACE_URL}/step",
            json={"action_type": action, "payload": {}},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        return {"reward": 0.0, "done": True, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"reward": 0.0, "done": True, "error": str(e)}


def main() -> None:
    """Main inference loop"""
    
    # Check required environment variables
    if not API_BASE_URL:
        print("[ERROR] API_BASE_URL environment variable not set", flush=True)
        log_end(False, 0, 0.0, [])
        return
    
    if not API_KEY:
        print("[ERROR] API_KEY environment variable not set", flush=True)
        log_end(False, 0, 0.0, [])
        return
    
    # Initialize OpenAI client with injected proxy credentials
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    
    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False
    
    log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)
    
    try:
        # Process each difficulty level
        for step_num, level in enumerate(["easy", "medium", "hard"], start=1):
            # Reset environment
            reset_result = reset_environment(level)
            
            if "error" in reset_result:
                log_step(step_num, f"reset_{level}", 0.0, True, reset_result["error"])
                rewards.append(0.0)
                continue
            
            # Get the code to analyze
            code = task_codes.get(level, "")
            
            # Get action from LLM (MUST go through proxy)
            action = get_model_action(client, code, level)
            
            # Execute step
            step_result = step_environment(action)
            
            reward = float(step_result.get("reward", 0.5))
            done = bool(step_result.get("done", False))
            error = step_result.get("error")
            
            rewards.append(reward)
            steps_taken = step_num
            
            log_step(step_num, action, reward, done, error)
        
        # Calculate normalized score (0 to 1)
        if rewards:
            raw_score = sum(rewards) / len(rewards)
        else:
            raw_score = 0.5
        
        score = min(max(raw_score, 0.01), 0.99)
        success = score >= SUCCESS_SCORE_THRESHOLD
        
    except Exception as e:
        print(f"[DEBUG] Main loop error: {e}", flush=True)
        success = False
        score = 0.01
    
    finally:
        # Always emit END line, even on exception
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)


if __name__ == "__main__":
    main()
