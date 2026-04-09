from tasks import TASKS
from graders import GRADERS


class CodeAnalysisEnv:
    def __init__(self):
        self.tasks = TASKS
        self.current_task = None
        self.current_level = None

    def list_tasks(self):
        return self.tasks

    def reset(self, level="easy"):
        """Reset environment for a specific task level"""
        for task in self.tasks:
            if task["id"] == level:
                self.current_task = task
                self.current_level = level
                return {
                    "task_id": task["id"],
                    "difficulty": task["difficulty"],
                    "objective": task["objective"],
                    "status": "ready"
                }
        return {"error": "Task not found"}

    def step(self, action_type, payload=None):
        """
        Execute a step and grade the prediction
        
        Args:
            action_type: The action taken (should match difficulty)
            payload: Dictionary containing 'issue' and 'suggestions'
        """
        if payload is None:
            payload = {}
        
        # Validate action matches difficulty
        expected_actions = {
            "easy": "analyze_syntax",
            "medium": "analyze_runtime",
            "hard": "security_scan"
        }
        
        expected = expected_actions.get(self.current_level)
        if expected and action_type != expected:
            return {
                "reward": 0.0,
                "done": True,
                "info": {
                    "error": f"Wrong action for {self.current_level} level. Expected {expected}, got {action_type}"
                }
            }
        
        # Get the appropriate grader
        if self.current_level and self.current_level in GRADERS:
            grader = GRADERS[self.current_level]
            
            try:
                # Grade the prediction
                score = grader(payload)
                return {
                    "reward": float(score),
                    "done": True,
                    "info": {
                        "score": score,
                        "level": self.current_level,
                        "message": f"Analysis graded for {self.current_level} task"
                    }
                }
            except Exception as e:
                return {
                    "reward": 0.0,
                    "done": True,
                    "info": {"error": f"Grading failed: {str(e)}"}
                }
        else:
            return {
                "reward": 0.0,
                "done": True,
                "info": {"error": f"No grader found for level: {self.current_level}"}
            }

    def state(self):
        """Return current environment state"""
        if not self.current_task:
            return {
                "status": "not_initialized",
                "available_tasks": [task["id"] for task in self.tasks]
            }
        
        return {
            "status": "active",
            "task_id": self.current_task["id"],
            "difficulty": self.current_task["difficulty"],
            "objective": self.current_task["objective"],
            "grader_available": self.current_level in GRADERS
        }
