from tasks import TASKS
from graders import GRADERS


class CodeReviewEnv:
    def __init__(self):
        self.tasks = TASKS
        self.current_task = None
        self.current_level = None
        self.step_count = 0

    def list_tasks(self):
        """
        REQUIRED BY VALIDATOR: Returns all tasks with their graders
        """
        tasks_list = []
        for task in self.tasks:
            tasks_list.append({
                "id": task["id"],
                "name": task["name"],
                "difficulty": task["difficulty"],
                "objective": task["objective"],
                "grader": task["grader"]  # CRITICAL: Must include this
            })
        return tasks_list

    def grade(self, task_id, prediction):
        """
        REQUIRED BY VALIDATOR: Grades a prediction for a specific task
        Returns a score between 0 and 1
        """
        # Find the task
        task = None
        for t in self.tasks:
            if t["id"] == task_id:
                task = t
                break
        
        if not task:
            return 0.5
        
        # Get the grader function
        grader_name = task["grader"]
        grader_func = GRADERS.get(grader_name)
        
        if not grader_func:
            return 0.5
        
        try:
            score = grader_func(prediction)
            # Ensure score is between 0.01 and 0.99
            if score >= 1.0:
                score = 0.99
            if score <= 0.0:
                score = 0.01
            return score
        except Exception:
            return 0.5

    def reset(self, level="easy"):
        """Reset environment"""
        for task in self.tasks:
            if task["id"] == level:
                self.current_task = task
                self.current_level = level
                self.step_count = 0
                return {
                    "task_id": task["id"],
                    "difficulty": task["difficulty"],
                    "code": task.get("sample_code", ""),
                    "status": "reset"
                }
        return {"error": f"Task '{level}' not found"}

    def step(self, action):
        """Execute a step"""
        self.step_count += 1
        
        # Create prediction from action
        prediction = {
            "issue": action.get("comment", ""),
            "suggestions": [action.get("comment", "")]
        }
        
        # Grade the prediction
        score = self.grade(self.current_level, prediction)
        
        return {
            "reward": score,
            "done": True,
            "info": {"score": score, "step": self.step_count}
        }

    def state(self):
        """Get current state"""
        if not self.current_task:
            return {"status": "not_initialized"}
        return {
            "status": "active",
            "current_task": self.current_level,
            "step_count": self.step_count
        }

    def close(self):
        """Cleanup"""
        pass
