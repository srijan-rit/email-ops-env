import asyncio
import os
import json
from typing import List
from openai import OpenAI
from env.email_env import EmailOpsEnv
from env.models import Action

# =========================
# ENV CONFIG (MANDATORY)
# =========================
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.getenv("HF_TOKEN")
API_KEY = os.getenv("API_KEY")  # MUST use this

MAX_STEPS = 10
MAX_TOTAL_REWARD = 10
SUCCESS_SCORE_THRESHOLD = 0.5

client = OpenAI(
    base_url=API_BASE_URL,
    api_key=API_KEY
)

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
# FALLBACK POLICY
# =========================
def fallback_policy(obs):
    emails = obs.inbox

    # prioritize urgent + important
    for e in sorted(emails, key=lambda x: -x.urgency):
        if e.archived or e.replied:
            continue
        if e.category in ["complaint", "inquiry"]:
            return Action(action_type="send_reply", email_id=e.id)

    # archive spam
    for e in emails:
        if e.archived or e.replied:
            continue
        if e.category == "spam":
            return Action(action_type="archive", email_id=e.id)

    # fallback
    for e in emails:
        if not (e.archived or e.replied):
            return Action(action_type="archive", email_id=e.id)

    return Action(action_type="archive", email_id=None)


# =========================
# RUN SINGLE TASK
# =========================
async def run_task(task_name: str):
    env = EmailOpsEnv(task_name=task_name)

    history: List[str] = []
    rewards: List[float] = []
    steps_taken = 0
    success = False
    score = 0.0

    log_start(task=task_name, env="email_ops_env", model=MODEL_NAME)

    try:
        result = await env.reset()

        # FORCE LLM CALL
        try:
            client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": "Respond with OK"}],
                temperature=0
            )
        except Exception:
            pass

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
                        You are an email assistant.

                        Inbox:
                        {[{
                            "id": e.id,
                            "subject": e.subject,
                            "category": e.category,
                            "urgency": e.urgency
                        } for e in obs.inbox]}

                        Rules:
                        - spam → archive
                        - complaint/inquiry → send_reply
                        - urgency >= 4 → prioritize

                        Return ONLY JSON:
                        {{"action_type": "...", "email_id": "..."}}
                        """

                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0
                )
                # print(response)
                content = response.choices[0].message.content.strip()
                data = json.loads(content)
                action = Action(**data)

            except Exception:
                print("Fallback")
                action = fallback_policy(obs)
                content = str(action)

            # =========================
            # STEP
            # =========================
            result = await env.step(action)

            reward = result["reward"] or 0.0
            done = result["done"]

            rewards.append(reward)
            steps_taken = step
            last_reward = reward

            log_step(step=step, action=content, reward=reward, done=done, error=None)

            history.append(f"Step {step}: {content} -> reward {reward:+.2f}")

            if done:
                break

        # =========================
        # SCORE
        # =========================
        score = sum(rewards) / MAX_TOTAL_REWARD if MAX_TOTAL_REWARD > 0 else 0.0
        score = min(max(score, 0.0), 1.0)
        success = score >= SUCCESS_SCORE_THRESHOLD

    finally:
        try:
            await env.close()
        except Exception as e:
            print(f"[DEBUG] env.close() error: {e}", flush=True)

        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)


# =========================
# MAIN (MULTI-TASK)
# =========================
async def main():
    tasks = [
        "spam_filter_easy",
        "priority_inbox",
        "customer_support_ops"
    ]

    for task in tasks:
        await run_task(task)


if __name__ == "__main__":
    asyncio.run(main())