# api/server.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from env.environment import CodeReviewEnv

app = FastAPI()
env = CodeReviewEnv()

@app.get("/")
async def root():
    return {"status": "running", "name": "Code Review Assistant"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/reset")
async def reset(level: str = "easy"):
    return env.reset(level)

@app.post("/step")
async def step(action: dict):
    return env.step(action)

@app.get("/state")
async def state():
    return env.state()

@app.get("/tasks")
async def get_tasks():
    return {"tasks": env.list_tasks()}