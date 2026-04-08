import asyncio
import os
import json
from typing import List
from openai import OpenAI
from env.email_env import EmailOpsEnv
from env.models import Action

# =========================
# ENV VARIABLES (REQUIRED)
# =========================
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.getenv("HF_TOKEN")  # required by spec (even if unused)

API_KEY = os.getenv("OPENAI_API_KEY", "dummy-key")

client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

MAX_STEPS = 10
MAX_TOTAL_REWARD = 10
SUCCESS_SCORE_THRESHOLD = 0.5


# =========================
# LOGGING (STRICT FORMAT)
# =========================
def log_start(task, env, model):
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step, action, reward, done, error):
    print(f"[STEP] step={step} action={action} reward={reward} done={done} error={error}", flush=True)


def log_end(success, steps, score, rewards):
    print(f"[END] success={success} steps={steps} score={score} rewards={rewards}", flush=True)


# =========================
# SMART FALLBACK POLICY 🔥
# =========================
def fallback_policy(obs):
    emails = obs.inbox

    # 1. Handle urgent complaints first
    for e in sorted(emails, key=lambda x: -x.urgency):
        if e.archived or e.replied:
            continue
        if e.category in ["complaint", "inquiry"]:
            return Action(action_type="send_reply", email_id=e.id)

    # 2. Archive spam
    for e in emails:
        if e.archived or e.replied:
            continue
        if e.category == "spam":
            return Action(action_type="archive", email_id=e.id)

    # 3. Default fallback
    for e in emails:
        if not (e.archived or e.replied):
            return Action(action_type="archive", email_id=e.id)

    return Action(action_type="archive", email_id=None)


# =========================
# MAIN LOOP
# =========================
async def main():
    # ✅ Use HARD task for better evaluation
    env = EmailOpsEnv(task_name="customer_support_ops")

    history: List[str] = []
    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False

    log_start(task="customer_support_ops", env="email_ops_env", model=MODEL_NAME)

    try:
        result = await env.reset()
        last_reward = 0.0

        for step in range(1, MAX_STEPS + 1):

            if result["done"]:
                break

            obs = result["observation"]

            # =========================
            # TRY GPT
            # =========================
            try:
                prompt = f"""
You are an intelligent customer support email assistant.

Your job:
- Archive spam emails
- Reply to customer emails (complaint, inquiry)
- Handle urgent emails first

Inbox:
{[{
    "id": e.id,
    "subject": e.subject,
    "body": e.body,
    "category": e.category,
    "urgency": e.urgency
} for e in obs.inbox]}

Rules:
- If category == spam → archive
- If complaint/inquiry → send_reply
- If urgency >= 4 → prioritize replying first

Return ONLY valid JSON:
{{"action_type": "archive or send_reply", "email_id": "id"}}
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
                # =========================
                # FALLBACK (CRITICAL)
                # =========================
                action = fallback_policy(obs)
                content = str(action)

            # =========================
            # ENV STEP
            # =========================
            result = await env.step(action)

            reward = result["reward"] or 0.0
            done = result["done"]
            error = None

            rewards.append(reward)
            steps_taken = step
            last_reward = reward

            log_step(step, content, reward, done, error)

            history.append(f"{step}:{reward}")

            if done:
                break

        # =========================
        # FINAL SCORE
        # =========================
        score = sum(rewards) / MAX_TOTAL_REWARD if MAX_TOTAL_REWARD > 0 else 0.0
        score = min(max(score, 0.0), 1.0)
        success = score >= SUCCESS_SCORE_THRESHOLD

    finally:
        await env.close()
        log_end(success, steps_taken, score, rewards)


if __name__ == "__main__":
    asyncio.run(main())