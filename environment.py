from models import Observation, EnvState
from tasks import TASKS
from graders import grade_action


class CodeAnalysisEnv:
    def __init__(self):
        self.task = TASKS["easy"]
        self.step_count = 0
        self.total_reward = 0.0
        self.done = False

    def reset(self, level="easy"):
        self.task = TASKS[level]
        self.step_count = 0
        self.total_reward = 0.0
        self.done = False
        return self.state()

    def step(self, action):
        reward, done, feedback = grade_action(self.task, action)

        self.step_count += 1
        self.total_reward += reward
        self.done = done

        return Observation(
            code=self.task["code"],
            difficulty=self.task["difficulty"],
            reward=reward,
            done=done,
            feedback=feedback
        )

    def state(self):
        return EnvState(
            task_id=self.task["id"],
            difficulty=self.task["difficulty"],
            step_count=self.step_count,
            total_reward=self.total_reward,
            done=self.done
        )
