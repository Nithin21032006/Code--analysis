from tasks import TASKS
from graders import GRADERS


class CodeReviewEnv:
    def __init__(self):
        self.tasks = TASKS
        self.current_task = None
        self.current_level = None
        self.step_count = 0

    def reset(self, level="easy"):
        """Reset environment"""
        for task in self.tasks:
            if task["id"] == level:
                self.current_task = task
                self.current_level = level
                self.step_count = 0
                return {
                    "observation": {
                        "code": task.get("sample_code", ""),
                        "difficulty": task["difficulty"],
                        "task_id": task["id"]
                    },
                    "reward": 0.0,
                    "done": False,
                    "info": {}
                }
        return {"error": "Task not found"}

    def step(self, action):
        """Execute step"""
        self.step_count += 1
        
        # Get the grader for current task
        grader_func = GRADERS.get(self.current_level)
        
        if grader_func:
            # Create prediction from action
            prediction = {
                "issue": action.get("comment", ""),
                "suggestions": [action.get("comment", "")]
            }
            score = grader_func(prediction)
        else:
            score = 0.50
        
        return {
            "observation": {
                "code": self.current_task.get("sample_code", ""),
                "difficulty": self.current_level,
                "step": self.step_count
            },
            "reward": score,
            "done": True,
            "info": {"score": score}
        }

    def state(self):
        """Get current state"""
        if not self.current_task:
            return {"state": "not_initialized"}
        return {
            "state": "active",
            "current_task": self.current_level,
            "step_count": self.step_count
        }

    def close(self):
        """Cleanup"""
        pass


# These MUST be available at module level for validator to find
def get_tasks():
    return TASKS

def get_graders():
    return GRADERS
