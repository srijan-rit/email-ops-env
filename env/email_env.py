from typing import List
from .models import Observation, Action, Email
from .tasks import generate_emails
from .graders import grade_easy, grade_medium, grade_hard


class EmailOpsEnv:

    def __init__(self, task_name="spam_filter_easy"):
        self.task_name = task_name
        self.emails: List[Email] = []
        self.step_count = 0
        self.max_steps = 10

    async def reset(self):
        self.emails = generate_emails(self.task_name)
        self.step_count = 0

        return self._get_obs(0.0, False)

    async def step(self, action: Action):
        self.step_count += 1
        reward = 0.0

        email = next((e for e in self.emails if e.id == action.email_id), None)

        if email:
            if action.action_type == "archive":
                email.archived = True
                reward = 0.3 if email.category == "spam" else -0.2

            elif action.action_type == "send_reply":
                email.replied = True
                reward = 0.3 if email.category != "spam" else -0.3

        reward = max(min(reward, 1.0), -1.0)

        done = self.step_count >= self.max_steps or self._all_done()

        if done:
            final_score = self._grade()
            return self._get_obs(final_score, True)

        return self._get_obs(reward, False)

    def _all_done(self):
        return all(e.archived or e.replied for e in self.emails)

    def _grade(self):
        if self.task_name == "spam_filter_easy":
            return grade_easy(self.emails)
        elif self.task_name == "priority_inbox":
            return grade_medium(self.emails)
        else:
            return grade_hard(self.emails)

    def _get_obs(self, reward, done):
        return {
            "observation": Observation(
                inbox=self.emails,
                current_email_id=None,
                draft_response=None,
                echoed_message=f"Step {self.step_count}"
            ),
            "reward": reward,
            "done": done,
            "info": {}
        }

    def state(self):
        return {
            "remaining": len([e for e in self.emails if not (e.archived or e.replied)]),
            "step": self.step_count
        }

    async def close(self):
        pass