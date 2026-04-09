#!/usr/bin/env python3
"""
Inference Script for Code Review Assistant
Must follow OpenEnv specification exactly
"""

import os
import sys
import json
import requests
from typing import List, Optional, Dict, Any

# Environment variables with defaults (only for API_BASE_URL and MODEL_NAME)
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN", "")
API_KEY = os.getenv("API_KEY", HF_TOKEN)

# Your Space URL - where your environment is deployed
SPACE_URL = os.getenv("SPACE_URL", "https://nithu007-code-lens.hf.space")

# Task configuration
TASK_NAME = "code_review_assistant"
BENCHMARK = "code_review_env"
MAX_STEPS = 10
SUCCESS_SCORE_THRESHOLD = 0.5


def log_start(task: str, env: str, model: str) -> None:
    """Emit START line - exactly one at episode begin"""
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    """Emit STEP line - one per step"""
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}", flush=True)


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    """Emit END line - after environment closes"""
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)


def reset_environment(level: str) -> Dict[str, Any]:
    """Reset the environment via HTTP"""
    try:
        response = requests.post(
            f"{SPACE_URL}/reset",
            params={"level": level},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}


def step_environment(action: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a step via HTTP"""
    try:
        response = requests.post(
            f"{SPACE_URL}/step",
            json=action,
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"reward": 0.0, "done": True, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"reward": 0.0, "done": True, "error": str(e)}


def get_llm_response(prompt: str) -> str:
    """Get response from LLM using OpenAI client"""
    try:
        # Import OpenAI only when needed
        from openai import OpenAI
        
        client = OpenAI(
            base_url=API_BASE_URL,
            api_key=API_KEY
        )
        
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a code review assistant. Analyze code and provide review comments."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=200,
            timeout=30
        )
        
        return response.choices[0].message.content or ""
    except Exception as e:
        print(f"[DEBUG] LLM error: {e}", flush=True)
        return ""


def main():
    """Main inference loop"""
    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False
    
    # Check if Space is reachable
    try:
        health_response = requests.get(f"{SPACE_URL}/health", timeout=10)
        if health_response.status_code != 200:
            print(f"[DEBUG] Health check failed: {health_response.status_code}", flush=True)
    except Exception as e:
        print(f"[DEBUG] Cannot reach Space: {e}", flush=True)
    
    log_start(TASK_NAME, BENCHMARK, MODEL_NAME)
    
    try:
        # Process each difficulty level
        levels = ["easy", "medium", "hard"]
        
        for level_idx, level in enumerate(levels, start=1):
            # Reset environment for this level
            reset_result = reset_environment(level)
            
            if "error" in reset_result:
                log_step(level_idx, f"reset_{level}", 0.0, True, reset_result["error"])
                rewards.append(0.0)
                continue
            
            # Get the code to review
            observation = reset_result
            code = observation.get("code", "")
            
            if not code:
                # Try to get code from sample_pr in tasks
                code = f"Sample {level} level code for review"
            
            # Create prompt for LLM
            prompt = f"""You are reviewing code for a {level} difficulty task.
            
Code to review:
{code}

Provide a review comment identifying any issues. Be specific about line numbers if possible.
Return your review as a JSON object with: action_type, comment, line_number (optional), severity.
Action types: review, suggest_fix, approve, reject
Severity: nitpick, warning, error, critical

Example: {{"action_type": "review", "comment": "Missing colon", "line_number": 1, "severity": "error"}}"""
            
            # Get LLM response
            llm_response = get_llm_response(prompt)
            
            # Parse LLM response or use default action
            try:
                # Try to parse JSON from response
                if "{" in llm_response:
                    start = llm_response.find("{")
                    end = llm_response.rfind("}") + 1
                    action = json.loads(llm_response[start:end])
                else:
                    # Default action based on level
                    action = {
                        "action_type": "review",
                        "comment": f"Reviewing {level} code",
                        "severity": "warning"
                    }
            except:
                action = {
                    "action_type": "review",
                    "comment": f"Found potential issues in {level} code",
                    "severity": "warning"
                }
            
            # Execute step
            step_result = step_environment(action)
            
            reward = float(step_result.get("reward", 0.5))
            done = bool(step_result.get("done", False))
            error = step_result.get("error")
            
            rewards.append(reward)
            steps_taken = level_idx
            
            log_step(level_idx, action.get("action_type", "review"), reward, done, error)
            
            if done:
                continue
        
        # Calculate final score (average of all rewards)
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
        log_end(success, steps_taken, score, rewards)


if __name__ == "__main__":
    main()
