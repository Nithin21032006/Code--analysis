from tasks import TASKS
from graders import GRADERS


class CodeReviewEnv:
    def __init__(self):
        self.tasks = TASKS
        self.current_task = None
        self.current_level = None
        self.step_count = 0
        self.issues_found = []

    def list_tasks(self):
        """Return all available tasks - validator calls this"""
        tasks_list = []
        for task in self.tasks:
            tasks_list.append({
                "id": task["id"],
                "name": task["name"],
                "difficulty": task["difficulty"],
                "objective": task["objective"],
                "grader": task["grader"]  # CRITICAL: Must include grader field
            })
        return tasks_list

    def get_grader(self, level):
        """Get grader function for a specific level"""
        for task in self.tasks:
            if task["id"] == level:
                grader_name = task["grader"]
                if grader_name in GRADERS:
                    return GRADERS[grader_name]
        return None

    def reset(self, level="easy"):
        """Reset environment for a specific level/task"""
        for task in self.tasks:
            if task["id"] == level:
                self.current_task = task
                self.current_level = level
                self.step_count = 0
                self.issues_found = []
                
                return {
                    "task_id": task["id"],
                    "name": task["name"],
                    "difficulty": task["difficulty"],
                    "objective": task["objective"],
                    "code": task.get("sample_code", ""),
                    "grader": task["grader"],  # Include grader info
                    "status": "reset"
                }
        
        return {"error": f"Task '{level}' not found"}

    def grade(self, level, prediction):
        """Grade a prediction - validator calls this for each task"""
        grader_func = self.get_grader(level)
        
        if not grader_func:
            return {
                "task_id": level,
                "score": 0.5,
                "error": f"Grader not found for {level}"
            }
        
        try:
            score = grader_func(prediction)
            # Ensure score is strictly between 0 and 1
            score = max(0.01, min(score, 0.99))
            
            return {
                "task_id": level,
                "score": score,
                "status": "graded"
            }
        except Exception as e:
            return {
                "task_id": level,
                "score": 0.5,
                "error": str(e)
            }

    def step(self, action_type, payload=None):
        """Execute a step"""
        if payload is None:
            payload = {}
        
        self.step_count += 1
        
        # Expected actions for each level
        expected_actions = {
            "easy": "analyze_syntax",
            "medium": "analyze_runtime",
            "hard": "security_scan"
        }
        
        expected = expected_actions.get(self.current_level)
        
        if expected and action_type != expected:
            return {
                "reward": 0.05,
                "done": True,
                "info": {"error": f"Wrong action. Expected {expected}, got {action_type}"}
            }
        
        # Create prediction for grading
        prediction = {
            "issue": payload.get("issue", ""),
            "suggestions": payload.get("suggestions", [])
        }
        
        # Grade the prediction
        grade_result = self.grade(self.current_level, prediction)
        
        return {
            "reward": grade_result.get("score", 0.5),
            "done": True,
            "info": {
                "message": f"Analysis completed for {self.current_level}",
                "score": grade_result.get("score", 0.5)
            }
        }

    def state(self):
        """Get current state"""
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
            "name": self.current_task.get("name"),
            "difficulty": self.current_task.get("difficulty"),
            "objective": self.current_task.get("objective"),
            "code": self.current_task.get("sample_code", ""),
            "step_count": self.step_count,
            "issues_found": len(self.issues_found)
        }
    
    def close(self):
        """Clean up resources"""
        pass
