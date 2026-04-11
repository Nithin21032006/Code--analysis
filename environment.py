from tasks import TASKS
from graders import GRADERS


class CodeReviewEnv:
    def __init__(self):
        self.tasks = TASKS if 'TASKS' in dir() else []
        self.current_level = None
        self.step_count = 0

    def reset(self, level="easy"):
        """Reset environment"""
        self.current_level = level
        self.step_count = 0
        return {
            "status": "reset",
            "level": level,
            "code": self._get_sample_code(level)
        }

    def step(self, action):
        """Execute a step"""
        self.step_count += 1
        
        # Get prediction from action
        prediction = {
            "issue": action.get("comment", "") if isinstance(action, dict) else str(action)
        }
        
        # Grade based on current level
        score = self._grade(self.current_level, prediction)
        
        return {
            "reward": score,
            "done": True,
            "info": {"step": self.step_count}
        }

    def state(self):
        """Get current state"""
        return {
            "status": "active",
            "current_level": self.current_level,
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
            # Ensure score is between 0.10 and 0.99
            if score >= 1.0:
                score = 0.99
            if score <= 0.0:
                score = 0.10
            return score
        return 0.50

    def _get_sample_code(self, level):
        """Get sample code for each level"""
        samples = {
            "easy": "def add(a,b)\n    return a+b",
            "medium": "arr = [1,2,3]\nfor i in range(5):\n    print(arr[i])",
            "hard": 'query = "SELECT * FROM users WHERE id=" + user_input'
        }
        return samples.get(level, "")

    def close(self):
        """Cleanup"""
        pass


# Import grader functions for direct access
from graders import grade_easy, grade_medium, grade_hard
