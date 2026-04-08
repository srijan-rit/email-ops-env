import uuid
from typing import Tuple
from env.models import Observation, Action, StepResult
from env.tasks import load_task
from env.graders import grade_task


class EmailOpsEnv:

    def __init__(self, task_name: str):
        self.task_name = task_name
        self.state = None
        self.steps = 0
        self.max_steps = 20

    async def reset(self) -> StepResult:
        self.state = load_task(self.task_name)
        self.steps = 0

        obs = Observation(
            inbox=self.state["emails"],
            echoed_message="Environment reset"
        )

        return StepResult(observation=obs, reward=0.0, done=False)

    async def step(self, action: Action) -> StepResult:
        self.steps += 1
        reward = 0.0

        emails = self.state["emails"]

        # Apply action
        if action.action_type == "archive":
            for e in emails:
                if e.id == action.email_id:
                    if e.is_spam:
                        reward += 0.2
                    else:
                        reward -= 0.3
                    e.archived = True

        elif action.action_type == "classify":
            for e in emails:
                if e.id == action.email_id:
                    if e.category == action.content:
                        reward += 0.2
                    else:
                        reward -= 0.2

        elif action.action_type == "draft_reply":
            reward += 0.1

        elif action.action_type == "send_reply":
            for e in emails:
                if e.id == action.email_id:
                    e.replied = True
                    reward += 0.3

        # Done condition
        done = self.steps >= self.max_steps

        # Final grading bonus
        if done:
            final_score = grade_task(self.task_name, self.state)
            reward += final_score

        obs = Observation(
            inbox=emails,
            echoed_message=f"Step {self.steps} executed"
        )

        return StepResult(observation=obs, reward=reward, done=done)

    async def state(self):
        return self.state

    async def close(self):
        pass