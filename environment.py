# environment.py
from tasks import TASKS, get_task, get_all_tasks
from graders import GRADERS, ALL_GRADERS


class CodeAnalysisEnv:
    def __init__(self):
        self.tasks = TASKS
        self.current_task = None
        self.current_level = None
        self.step_count = 0

    def list_tasks(self):
        """
        Enumerate all tasks - validator calls this
        Must return list of tasks with grader information
        """
        tasks_list = []
        for task in self.tasks:
            tasks_list.append({
                "id": task["id"],
                "name": task["name"],
                "difficulty": task["difficulty"],
                "objective": task["objective"],
                "grader_name": task.get("grader_name", f"{task['id']}_grader")
            })
        return tasks_list

    def get_grader(self, task_id):
        """Get grader function for a specific task"""
        task = get_task(task_id)
        if task:
            grader_name = task.get("grader_name", f"{task_id}_grader")
            return GRADERS.get(grader_name)
        return None

    def reset(self, level="easy"):
        """Reset environment for a specific level/task"""
        task = get_task(level)
        if task:
            self.current_task = task
            self.current_level = level
            self.step_count = 0
            
            return {
                "task_id": task["id"],
                "difficulty": task["difficulty"],
                "objective": task["objective"],
                "code": task.get("sample_code", ""),
                "status": "reset",
                "grader_name": task.get("grader_name", f"{level}_grader")
            }
        
        return {"error": f"Task '{level}' not found"}

    def grade(self, level, prediction):
        """
        Grade a prediction - validator calls this for each task
        Must return score strictly between 0 and 1
        """
        # Find the grader function
        grader_func = self.get_grader(level)
        
        if not grader_func:
            # Fallback: try direct mapping
            if level == "easy":
                from graders import easy_grader
                grader_func = easy_grader
            elif level == "medium":
                from graders import medium_grader
                grader_func = medium_grader
            elif level == "hard":
                from graders import hard_grader
                grader_func = hard_grader
            else:
                return {
                    "task_id": level,
                    "score": 0.50,  # Default middle score
                    "error": f"No grader found for task '{level}'"
                }
        
        try:
            # Execute the grader
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
                "score": 0.50,
                "error": f"Grading error: {str(e)}"
            }

    def step(self, action_type, payload=None):
        """Execute a step (for main.py)"""
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
            return {
                "reward": 0.05,  # Low but > 0
                "done": True,
                "info": {"error": f"Wrong action. Expected {expected}, got {action_type}"}
            }
        
        # Grade using the grade method
        prediction = {
            "issue": payload.get("issue", ""),
            "suggestions": payload.get("suggestions", [])
        }
        
        result = self.grade(self.current_level, prediction)
        
        if "score" in result:
            return {
                "reward": result["score"],
                "done": True,
                "info": {
                    "message": f"Analysis completed for {self.current_level}",
                    "score": result["score"]
                }
            }
        else:
            return {
                "reward": 0.50,
                "done": True,
                "info": {"error": result.get("error", "Grading failed")}
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
            "difficulty": self.current_task.get("difficulty"),
            "objective": self.current_task.get("objective"),
            "code": self.current_task.get("sample_code", ""),
            "step_count": self.step_count
        }
