import asyncio
import os
import json
from typing import List
from openai import OpenAI
from env.email_env import EmailOpsEnv
from env.models import Action

# REQUIRED ENV VARIABLES (with defaults)
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.getenv("HF_TOKEN")

API_KEY = os.getenv("OPENAI_API_KEY", "dummy-key")

client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

MAX_STEPS = 10
MAX_TOTAL_REWARD = 10
SUCCESS_SCORE_THRESHOLD = 0.5


def log_start(task, env, model):
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step, action, reward, done, error):
    print(f"[STEP] step={step} action={action} reward={reward} done={done} error={error}", flush=True)


def log_end(success, steps, score, rewards):
    print(f"[END] success={success} steps={steps} score={score} rewards={rewards}", flush=True)


def fallback_policy(obs):
    """Deterministic safe fallback (used if GPT fails)"""
    emails = obs.inbox

    for e in emails:
        if e.archived or e.replied:
            continue
        text = (e.subject + " " + e.body).lower()
        if "urgent" in text or "complaint" in text:
            return Action(action_type="send_reply", email_id=e.id)

    for e in emails:
        if e.archived or e.replied:
            continue
        text = (e.subject + " " + e.body).lower()
        if "offer" in text or "buy" in text or "click" in text:
            return Action(action_type="archive", email_id=e.id)

    for e in emails:
        if not e.archived:
            return Action(action_type="archive", email_id=e.id)

    return Action(action_type="archive", email_id=None)


async def main():
    env = EmailOpsEnv(task_name="multi_step")

    history: List[str] = []
    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False

    log_start(task="multi_step", env="email_ops_env", model=MODEL_NAME)

    try:
        result = await env.reset()
        last_reward = 0.0

        for step in range(1, MAX_STEPS + 1):
            if result.done:
                break

            obs = result.observation

            # -------- TRY GPT --------
            try:
                prompt = f"""
You are an email assistant.

Inbox:
{[{"id": e.id, "subject": e.subject, "body": e.body} for e in obs.inbox]}

Choose ONE action:
- archive
- send_reply

Return ONLY valid JSON:
{{"action_type": "...", "email_id": "..."}}
"""

                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0
                )

                content = response.choices[0].message.content.strip()
                data = json.loads(content)
                action = Action(**data)

            except Exception:
                # -------- FALLBACK --------
                action = fallback_policy(obs)
                content = str(action)

            result = await env.step(action)

            reward = result.reward or 0.0
            done = result.done
            error = None

            rewards.append(reward)
            steps_taken = step
            last_reward = reward

            log_step(step, content, reward, done, error)

            history.append(f"{step}:{reward}")

            if done:
                break

        score = sum(rewards) / MAX_TOTAL_REWARD if MAX_TOTAL_REWARD > 0 else 0.0
        score = min(max(score, 0.0), 1.0)
        success = score >= SUCCESS_SCORE_THRESHOLD

    finally:
        await env.close()
        log_end(success, steps_taken, score, rewards)


if __name__ == "__main__":
    asyncio.run(main())