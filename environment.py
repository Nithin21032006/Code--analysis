# env/environment.py
from env.tasks import TASKS
from env.graders import GRADERS


class CodeReviewEnv:
    def __init__(self):
        self.tasks = TASKS
        self.current_task = None
        self.current_level = None
        self.step_count = 0

    def list_tasks(self):
        """Return all tasks for validator"""
        return self.tasks

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
            "issue": action.get("comment", "") if isinstance(action, dict) else str(action)
        }
        
        # Grade the prediction
        score = self._grade(self.current_level, prediction)
        
        return {
            "reward": score,
            "done": True,
            "info": {"step": self.step_count}
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

    def _grade(self, level, prediction):
        """Internal grading method"""
        grader_map = {
            "easy": grade_easy,
            "medium": grade_medium,
            "hard": grade_hard
        }
        
        grader = grader_map.get(level)
        if grader:
            score = grader(prediction)
            if score >= 1.0:
                score = 0.99
            if score <= 0.0:
                score = 0.10
            return score
        return 0.50

    def close(self):
        """Cleanup"""
        pass


# Import grader functions
from env.graders import grade_easy, grade_medium, grade_hard