import asyncio
import os
from openai import OpenAI
from env.email_env import EmailOpsEnv
from env.models import Action
import json

API_BASE_URL = os.getenv("API_BASE_URL")
API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")

MAX_STEPS = 10
MAX_TOTAL_REWARD = 10
SUCCESS_SCORE_THRESHOLD = 0.5


def log_start(task, env, model):
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step, action, reward, done, error):
    print(f"[STEP] step={step} action={action} reward={reward} done={done} error={error}", flush=True)


def log_end(success, steps, score, rewards):
    print(f"[END] success={success} steps={steps} score={score} rewards={rewards}", flush=True)


def get_model_message(client, step, last_obs, last_reward, history):
    return "archive"  # simple baseline


async def main():
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

    env = EmailOpsEnv(task_name="multi_step")

    history = []
    rewards = []
    steps_taken = 0
    score = 0.0
    success = False

    log_start(task="multi_step", env="email_ops_env", model=MODEL_NAME)

    try:
        result = await env.reset()
        last_obs = result.observation.echoed_message
        last_reward = 0.0

        for step in range(1, MAX_STEPS + 1):
            if result.done:
                break

            obs = result.observation

            prompt = f"""
            You are an email assistant.

            Inbox:
            {[{"id": e.id, "subject": e.subject, "body": e.body} for e in obs.inbox]}

            Choose ONE action:
            - archive (for spam emails)
            - send_reply (for important emails)

            Return ONLY JSON:
            {{"action_type": "...", "email_id": "..."}}
            """

            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            print(response)

            content = response.choices[0].message.content.strip()

            try:
                data = json.loads(content)
                action = Action(**data)
            except Exception:
                # fallback if GPT messes up
                emails = obs.inbox
                email_id = emails[0].id if emails else None
                action = Action(action_type="archive", email_id=email_id)

            message = content

            result = await env.step(action)

            reward = result.reward or 0.0
            done = result.done
            error = None

            rewards.append(reward)
            steps_taken = step
            last_obs = result.observation.echoed_message
            last_reward = reward

            log_step(step, message, reward, done, error)

            history.append(f"{step}:{reward}")

            if done:
                break

        score = sum(rewards) / MAX_TOTAL_REWARD
        score = min(max(score, 0.0), 1.0)
        success = score >= SUCCESS_SCORE_THRESHOLD

    finally:
        await env.close()
        log_end(success, steps_taken, score, rewards)


if __name__ == "__main__":
    asyncio.run(main())