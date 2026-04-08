import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from env.email_env import EmailOpsEnv
from env.models import Action

app = FastAPI()

env = EmailOpsEnv(task_name="multi_step")


@app.get("/")
async def root():
    return {"status": "ok"}


@app.post("/reset")
async def reset():
    global env
    env = EmailOpsEnv(task_name="multi_step")
    return await env.reset()


@app.post("/step")
async def step(action: Action):
    global env
    return await env.step(action)