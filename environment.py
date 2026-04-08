from tasks import TASKS
from graders import GRADERS


class CodeAnalysisEnv:
    def __init__(self):
        self.tasks = TASKS
        self.current_task = None

    def list_tasks(self):
        return self.tasks

    def reset(self, level="easy"):
        for task in self.tasks:
            if task["id"] == level:
                self.current_task = task
                return {
                    "task_id": task["id"],
                    "difficulty": task["difficulty"],
                    "objective": task["objective"]
                }

        return {"error": "Task not found"}

    def grade(self, level, prediction):
        for task in self.tasks:
            if task["id"] == level:
                grader_name = task["grader"]
                grader_function = GRADERS[level]

                score = grader_function(prediction)

                return {
                    "task_id": level,
                    "score": score
                }

        return {"error": "Invalid task"}
