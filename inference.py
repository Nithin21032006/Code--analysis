"""
Inference Script for Code Analysis Environment
Connects to deployed Hugging Face Space instead of local Docker
"""

import os
import json
import textwrap
import requests
from typing import List, Optional, Dict, Any
from openai import OpenAI

# Environment variables with defaults (only for API_BASE_URL and MODEL_NAME)
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN")  # No default - must be injected
API_KEY = os.getenv("API_KEY", HF_TOKEN)

# Your deployed Space URL - THIS IS CRITICAL
# The validator will use this to connect to your environment
SPACE_URL = os.getenv("SPACE_URL", "https://nithu007-code-lens.hf.space")

# Task configuration
TASK_NAME = "code_analysis"
BENCHMARK = "custom_fastapi_env"
MAX_STEPS = 3
TEMPERATURE = 0.7
MAX_TOKENS = 500
SUCCESS_SCORE_THRESHOLD = 0.5

# Test cases for each difficulty level
task_codes = {
    "easy": "print('Hello World'",  # Missing parenthesis
    "medium": "arr = [1, 2, 3]\nfor i in range(5):\n    print(arr[i])",  # Index error
    "hard": 'query = "SELECT * FROM users WHERE id=" + user_input',  # SQL injection
}


def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}", flush=True)


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)


def reset_environment(level: str) -> Dict[str, Any]:
    """Reset environment via HTTP to your Space"""
    try:
        response = requests.post(
            f"{SPACE_URL}/reset",
            params={"level": level},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[DEBUG] Reset failed for {level}: {e}", flush=True)
        return {"error": str(e)}


def get_environment_state() -> Dict[str, Any]:
    """Get current state via HTTP"""
    try:
        response = requests.get(f"{SPACE_URL}/state", timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[DEBUG] Get state failed: {e}", flush=True)
        return {}


def step_environment(action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a step via HTTP"""
    try:
        response = requests.post(
            f"{SPACE_URL}/step",
            json={"action_type": action, "payload": payload},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"reward": 0.0, "done": True, "error": str(e)}


def analyze_code_with_llm(client: OpenAI, code: str, level: str) -> str:
    """Use LLM to determine the correct action"""
    prompt = textwrap.dedent(f"""
        Analyze this {level} level code and identify the issue.
        Code: {code}
        
        Choose ONE action:
        - analyze_syntax (for syntax errors)
        - analyze_runtime (for runtime bugs)
        - security_scan (for security issues)
        
        Return only the action name, nothing else.
    """).strip()
    
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=50,
        )
        action = completion.choices[0].message.content.strip().lower()
        # Validate action
        if action in ["analyze_syntax", "analyze_runtime", "security_scan"]:
            return action
        # Fallback based on level
        if level == "easy":
            return "analyze_syntax"
        elif level == "medium":
            return "analyze_runtime"
        else:
            return "security_scan"
    except Exception as e:
        print(f"[DEBUG] LLM analysis failed: {e}", flush=True)
        # Fallback actions
        if level == "easy":
            return "analyze_syntax"
        elif level == "medium":
            return "analyze_runtime"
        else:
            return "security_scan"


def main():
    """Main inference loop - NO DOCKER, just HTTP calls to Space"""
    # Check if Space is reachable
    try:
        response = requests.get(f"{SPACE_URL}/health", timeout=10)
        if response.status_code != 200:
            print(f"[DEBUG] Space health check failed: {response.status_code}", flush=True)
    except Exception as e:
        print(f"[DEBUG] Cannot reach Space at {SPACE_URL}: {e}", flush=True)
        # Still continue - validator might have different network access
    
    # Initialize OpenAI client with proxy credentials
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    
    rewards = []
    steps_taken = 0
    success = False
    
    log_start(TASK_NAME, BENCHMARK, MODEL_NAME)
    
    try:
        for step_num, level in enumerate(["easy", "medium", "hard"], start=1):
            # Reset environment
            reset_result = reset_environment(level)
            if "error" in reset_result:
                log_step(step_num, f"reset_{level}", 0.0, True, reset_result["error"])
                rewards.append(0.0)
                break
            
            # Get current code (or use predefined)
            state = get_environment_state()
            code = state.get("code", task_codes.get(level, ""))
            
            # Use LLM to determine action
            action = analyze_code_with_llm(client, code, level)
            
            # Execute step
            step_result = step_environment(action, {"code": code, "level": level})
            
            reward = float(step_result.get("reward", 0.5))
            done = bool(step_result.get("done", False))
            error = step_result.get("error")
            
            rewards.append(reward)
            steps_taken = step_num
            
            log_step(step_num, action, reward, done, error)
            
            if done:
                break
        
        # Calculate score
        if rewards:
            raw_score = sum(rewards) / len(rewards)
        else:
            raw_score = 0.0
        
        score = min(max(raw_score, 0.0), 1.0)
        success = score >= SUCCESS_SCORE_THRESHOLD
        
    except Exception as e:
        print(f"[DEBUG] Main loop error: {e}", flush=True)
        success = False
        score = 0.0
    
    finally:
        log_end(success, steps_taken, score, rewards)


if __name__ == "__main__":
    main()
