from pydantic import BaseModel
from typing import Dict, Any

class Action(BaseModel):
    action_type: str
    payload: Dict[str, Any] = {}

class Observation(BaseModel):
    code: str
    difficulty: str
    reward: float
    done: bool
    feedback: str

class EnvState(BaseModel):
    task_id: str
    difficulty: str
    step_count: int
    total_reward: float
    done: bool