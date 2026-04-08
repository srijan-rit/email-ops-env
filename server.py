from fastapi import FastAPI
from env.email_env import EmailOpsEnv
from env.models import Action

app = FastAPI()

env = EmailOpsEnv(task_name="multi_step")


@app.post("/reset")
async def reset():
    return await env.reset()


@app.post("/step")
async def step(action: Action):
    return await env.step(action)