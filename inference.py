import os
import json
from typing import List, Optional
from openai import OpenAI

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY")

TASK_NAME = "code_review_assistant"
BENCHMARK = "code_review_env"
MAX_STEPS = 15


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
    from environment import CodeReviewEnv
    
    env = CodeReviewEnv()
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    
    all_rewards = []
    tasks = ["easy", "medium", "hard"]
    
    log_start(TASK_NAME, BENCHMARK, MODEL_NAME)
    
    for task_idx, task_level in enumerate(tasks, 1):
        observation = env.reset(task_level)
        rewards = []
        
        for step in range(1, MAX_STEPS + 1):
            # Get agent action
            prompt = f"""You are reviewing a pull request. Task: {task_level}
PR Title: {observation['pr_title']}
Code: {observation['files_changed'][0]['content']}

Choose an action: review, suggest_fix, approve, or reject.
Respond with JSON: {{"action_type": "review", "comment": "...", "line_number": 1, "severity": "warning"}}
"""
            
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=200
            )
            
            try:
                action = json.loads(response.choices[0].message.content)
            except:
                action = {"action_type": "approve", "comment": "Looks good"}
            
            result = env.step(action)
            reward = result["reward"]
            done = result["done"]
            
            rewards.append(reward)
            log_step(step, action.get("action_type", "unknown"), reward, done)
            
            if done:
                break
        
        all_rewards.extend(rewards)
    
    total_score = sum(all_rewards) / len(all_rewards) if all_rewards else 0.5
    log_end(True, len(all_rewards), total_score, all_rewards)


if __name__ == "__main__":
    main()
