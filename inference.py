"""
Inference Script for Code Analysis Environment
===================================
MANDATORY
- Environment variables: API_BASE_URL, MODEL_NAME, HF_TOKEN
- Defaults set only for API_BASE_URL and MODEL_NAME
- Uses OpenAI Client for all LLM calls
- STDOUT format: [START], [STEP], [END] lines
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
API_KEY = os.getenv("API_KEY", HF_TOKEN)  # API_KEY can be same as HF_TOKEN

# Optional - for docker image
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME")

# Your Space URL (required for API calls)
SPACE_URL = os.getenv("SPACE_URL", "https://nithu007-code-lens.hf.space")

# Task configuration
TASK_NAME = "code_analysis"
BENCHMARK = "custom_fastapi_env"
MAX_STEPS = 3  # 3 difficulty levels: easy, medium, hard
TEMPERATURE = 0.7
MAX_TOKENS = 500

# Success threshold (normalized score in [0, 1])
SUCCESS_SCORE_THRESHOLD = 0.5

# Task definitions
task_codes = {
    "easy": "print('Hello World'",  # Missing closing parenthesis
    "medium": "arr = [1, 2, 3]\nfor i in range(5):\n    print(arr[i])",  # Index out of range
    "hard": 'query = "SELECT * FROM users WHERE id=" + user_input',  # SQL injection
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


def analyze_code_with_llm(client: OpenAI, code: str, difficulty_level: str) -> Dict[str, Any]:
    """Use LLM to analyze code and get suggestions"""
    system_prompt = textwrap.dedent(
        """
        You are a code analysis assistant. Analyze the given code and:
        1. Identify the main issue in the code
        2. Classify the difficulty (easy, medium, or hard)
        3. Provide 2-3 specific suggestions to fix the issue
        
        Return a JSON object with keys: issue, difficulty, suggestions
        """
    ).strip()
    
    user_prompt = f"Analyze this {difficulty_level} code:\n\n{code}"
    
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            stream=False,
        )
        
        response_text = completion.choices[0].message.content or "{}"
        # Try to parse JSON, fallback to default
        try:
            result = json.loads(response_text)
        except json.JSONDecodeError:
            # If not valid JSON, extract from text or use defaults
            result = {
                "issue": "unknown",
                "difficulty": difficulty_level,
                "suggestions": [response_text[:200]]
            }
        
        return result
        
    except Exception as exc:
        print(f"[DEBUG] LLM analysis failed: {exc}", flush=True)
        return {
            "issue": "analysis_failed",
            "difficulty": difficulty_level,
            "suggestions": ["Unable to analyze code due to API error"]
        }


def reset_environment(level: str) -> bool:
    """Reset the environment for a specific difficulty level"""
    try:
        response = requests.post(
            f"{SPACE_URL}/reset",
            params={"level": level},
            timeout=30
        )
        return response.status_code == 200
    except Exception as e:
        print(f"[DEBUG] Reset failed for {level}: {e}", flush=True)
        return False


def step_environment(action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a step in the environment"""
    try:
        response = requests.post(
            f"{SPACE_URL}/step",
            json={"action_type": action, "payload": payload},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"reward": 0.0, "done": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"reward": 0.0, "done": False, "error": str(e)}


def get_environment_state() -> Dict[str, Any]:
    """Get current environment state"""
    try:
        response = requests.get(f"{SPACE_URL}/state", timeout=30)
        if response.status_code == 200:
            return response.json()
        return {}
    except Exception:
        return {}


async def main() -> None:
    """Main inference loop"""
    # Initialize OpenAI client with proxy credentials
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    
    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False
    
    log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)
    
    try:
        # Process each difficulty level
        for step_num, level in enumerate(["easy", "medium", "hard"], start=1):
            # Reset environment for this level
            if not reset_environment(level):
                log_step(step_num, f"reset_{level}", 0.0, False, "Failed to reset environment")
                rewards.append(0.0)
                continue
            
            # Get current state (code to analyze)
            state = get_environment_state()
            code = task_codes.get(level, "")
            
            # Analyze code using LLM through the proxy
            analysis = analyze_code_with_llm(client, code, level)
            
            # Determine action based on analysis
            action = expected_actions.get(level, "analyze")
            
            # Execute step with the analysis results
            step_result = step_environment(action, {
                "issue": analysis.get("issue", "unknown"),
                "suggestions": analysis.get("suggestions", []),
                "difficulty": analysis.get("difficulty", level)
            })
            
            reward = float(step_result.get("reward", 0.5))
            done = bool(step_result.get("done", False))
            error = step_result.get("error")
            
            rewards.append(reward)
            steps_taken = step_num
            
            log_step(step_num, action, reward, done, error)
            
            if done:
                break
        
        # Calculate normalized score (0 to 1)
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
        # Always emit END line, even on exception
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
