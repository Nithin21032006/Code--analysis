from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from environment import CodeReviewEnv
from models import CodeReviewAction
import os

app = FastAPI(title="Code Review Assistant", description="OpenEnv for AI code review agents")

# Setup templates and static files
templates = Jinja2Templates(directory="templates")
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

env = CodeReviewEnv()

@app.get("/")
async def root(request: Request):
    """Root endpoint - serves your HTML template"""
    try:
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        return JSONResponse(content={"error": f"Template error: {str(e)}", "status": "fallback"})

@app.get("/health")
async def health():
    return {"status": "healthy", "environment": "code_review", "version": "1.0.0"}

@app.post("/reset")
async def reset(level: str = "easy"):
    try:
        obs = env.reset(level)
        return JSONResponse(content=obs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/step")
async def step(action: dict):
    try:
        result = env.step(action)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/state")
async def state():
    try:
        state = env.state()
        return JSONResponse(content=state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks")
async def get_tasks():
    """List all available tasks"""
    from tasks import TASKS
    tasks_list = []
    for task in TASKS:
        tasks_list.append({
            "id": task["id"],
            "name": task["name"],
            "difficulty": task["difficulty"],
            "objective": task["objective"]
        })
    return {"tasks": tasks_list}
