from tasks import TASKS
from graders import GRADERS


class CodeAnalysisEnv:
    def __init__(self):
        self.tasks = TASKS
        self.current_task = None
        self.current_code = ""
        self.current_level = None
        self.step_count = 0
        self.analysis_result = None

    def list_tasks(self):
        return self.tasks

    def reset(self, level="easy"):
        """Reset the environment for a specific difficulty level"""
        for task in self.tasks:
            if task["id"] == level:
                self.current_task = task
                self.current_level = level
                self.step_count = 0
                self.analysis_result = None
                self.current_code = self._get_sample_code(level)
                
                return {
                    "task_id": task["id"],
                    "difficulty": task["difficulty"],
                    "objective": task["objective"],
                    "code": self.current_code,
                    "status": "reset"
                }

        return {"error": "Task not found"}

    def step(self, action_type, payload=None):
        """
        Execute a step in the environment
        
        Args:
            action_type: Type of action (analyze_syntax, analyze_runtime, security_scan)
            payload: Additional data for the action
        """
        if payload is None:
            payload = {}
        
        self.step_count += 1
        
        # Default response
        result = {
            "reward": 0.0,
            "done": False,
            "info": {},
            "step": self.step_count
        }
        
        # Validate action type matches difficulty level
        if self.current_level == "easy" and action_type != "analyze_syntax":
            result["reward"] = 0.2
            result["info"] = {"error": f"Wrong action for easy level. Expected analyze_syntax, got {action_type}"}
            result["done"] = True
            return result
        
        elif self.current_level == "medium" and action_type != "analyze_runtime":
            result["reward"] = 0.2
            result["info"] = {"error": f"Wrong action for medium level. Expected analyze_runtime, got {action_type}"}
            result["done"] = True
            return result
        
        elif self.current_level == "hard" and action_type != "security_scan":
            result["reward"] = 0.2
            result["info"] = {"error": f"Wrong action for hard level. Expected security_scan, got {action_type}"}
            result["done"] = True
            return result
        
        # Grade the analysis based on the payload
        issue = payload.get("issue", "")
        suggestions = payload.get("suggestions", [])
        
        # Use the grader for the current level
        if self.current_level and self.current_level in GRADERS:
            grader_function = GRADERS[self.current_level]
            
            # Create prediction object for grader
            prediction = {
                "issue": issue,
                "suggestions": suggestions,
                "action": action_type
            }
            
            try:
                score = grader_function(prediction)
                result["reward"] = float(score)
                result["done"] = True
                result["info"] = {
                    "message": f"Analysis completed for {self.current_level} level",
                    "score": score,
                    "issue_identified": issue
                }
            except Exception as e:
                result["reward"] = 0.3
                result["done"] = True
                result["info"] = {"error": f"Grading failed: {str(e)}"}
        else:
            # Fallback grading if no grader found
            result["reward"] = 0.5
            result["done"] = True
            result["info"] = {"message": "Analysis completed with default grading"}
        
        self.analysis_result = result
        return result

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
            "status": "active" if not self.analysis_result else "completed",
            "task_id": self.current_task.get("id"),
            "difficulty": self.current_task.get("difficulty"),
            "objective": self.current_task.get("objective"),
            "code": self.current_code,
            "step_count": self.step_count,
            "analysis_completed": self.analysis_result is not None,
            "last_reward": self.analysis_result.get("reward") if self.analysis_result else None
        }

    def _get_sample_code(self, level):
        """Get sample code for each difficulty level"""
        sample_codes = {
            "easy": "print('Hello World'",  # Missing closing parenthesis
            "medium": "arr = [1, 2, 3]\nfor i in range(5):\n    print(arr[i])",  # Index out of range
            "hard": 'query = "SELECT * FROM users WHERE id=" + user_input'  # SQL injection
        }
        return sample_codes.get(level, "")
