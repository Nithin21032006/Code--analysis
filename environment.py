from tasks import TASKS
from graders import GRADERS


class CodeAnalysisEnv:
    def __init__(self):
        self.tasks = TASKS
        self.current_task = None
        self.current_level = None
        self.step_count = 0

    def list_tasks(self):
        return self.tasks

    def reset(self, level="easy"):
        """Reset the environment for a specific difficulty level"""
        for task in self.tasks:
            if task["id"] == level:
                self.current_task = task
                self.current_level = level
                self.step_count = 0
                
                return {
                    "task_id": task["id"],
                    "difficulty": task["difficulty"],
                    "objective": task["objective"],
                    "code": task.get("sample_code", ""),
                    "status": "reset"
                }
        
        return {"error": "Task not found"}

    def step(self, action_type, payload=None):
        """
        Execute a step in the environment
        """
        if payload is None:
            payload = {}
        
        self.step_count += 1
        
        # Validate action matches level
        expected_actions = {
            "easy": "analyze_syntax",
            "medium": "analyze_runtime",
            "hard": "security_scan"
        }
        
        expected = expected_actions.get(self.current_level)
        
        if expected and action_type != expected:
            # Return a low but non-zero score for wrong action
            return {
                "reward": 0.05,  # Strictly between 0 and 1
                "done": True,
                "info": {"error": f"Wrong action. Expected {expected}, got {action_type}"}
            }
        
        # Grade the prediction
        if self.current_level and self.current_level in GRADERS:
            grader_function = GRADERS[self.current_level]
            
            prediction = {
                "issue": payload.get("issue", ""),
                "suggestions": payload.get("suggestions", [])
            }
            
            try:
                score = grader_function(prediction)
                # Ensure score is strictly between 0 and 1
                score = min(max(score, 0.01), 0.99)
                
                return {
                    "reward": score,
                    "done": True,
                    "info": {
                        "message": f"Analysis completed for {self.current_level} level",
                        "score": score
                    }
                }
            except Exception as e:
                return {
                    "reward": 0.25,
                    "done": True,
                    "info": {"error": f"Grading failed: {str(e)}"}
                }
        
        # Default fallback - non-zero score
        return {
            "reward": 0.50,
            "done": True,
            "info": {"message": "Analysis completed with default grading"}
        }

    def state(self):
        """Get the current state of the environment"""
        if not self.current_task:
            return {
                "status": "not_initialized",
                "code": "",
                "difficulty": None,
                "step_count": 0
            }
        
        return {
            "status": "active",
            "task_id": self.current_task.get("id"),
            "difficulty": self.current_task.get("difficulty"),
            "objective": self.current_task.get("objective"),
            "code": self.current_task.get("sample_code", ""),
            "step_count": self.step_count
        }
