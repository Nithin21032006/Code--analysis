import os
import json
from fastapi import FastAPI, Request, Body
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from openai import OpenAI

from environment import CodeAnalysisEnv
from models import Action

app = FastAPI()
env = CodeAnalysisEnv()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Use injected proxy credentials safely
client = OpenAI(
    base_url=os.environ["API_BASE_URL"],
    api_key=os.environ["API_KEY"]
)


# ---------------- HOME ----------------
@app.get("/")
async def home(request: Request):
    try:
        state = env.state()

        if isinstance(state, dict):
            state_data = state
        else:
            state_data = state.dict()

        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "state": state_data
            }
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Home failed: {str(e)}"}
        )


# ---------------- TASK DISCOVERY ----------------
@app.get("/tasks")
async def get_tasks():
    return JSONResponse(content={
        "tasks": [
            {
                "id": "easy",
                "name": "Syntax Error Detection",
                "grader": True,
                "reward_range": [0.01, 0.99]
            },
            {
                "id": "medium",
                "name": "Runtime Bug Detection",
                "grader": True,
                "reward_range": [0.01, 0.99]
            },
            {
                "id": "hard",
                "name": "Security Vulnerability Detection",
                "grader": True,
                "reward_range": [0.01, 0.99]
            }
        ]
    })


# ---------------- RESET ----------------
@app.post("/reset")
async def reset(level: str = "easy"):
    try:
        result = env.reset(level)

        if isinstance(result, dict):
            return JSONResponse(content=result)

        return JSONResponse(content=result.dict())

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Reset failed: {str(e)}"}
        )


# ---------------- STEP ----------------
@app.post("/step")
async def step(action: Action):
    try:
        result = env.step(action)

        if isinstance(result, dict):
            return JSONResponse(content=result)

        return JSONResponse(content=result.dict())

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Step failed: {str(e)}"}
        )


# ---------------- STATE ----------------
@app.get("/state")
async def state():
    try:
        result = env.state()

        if isinstance(result, dict):
            return JSONResponse(content=result)

        return JSONResponse(content=result.dict())

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"State failed: {str(e)}"}
        )


# ---------------- ANALYZE ----------------
@app.post("/analyze")
async def analyze(data: dict = Body(...)):
    code = data.get("code", "")

    if not code.strip():
        return JSONResponse(content={
            "difficulty": "unknown",
            "suggestions": ["No code provided"]
        })

    try:
        response = client.chat.completions.create(
            model=os.environ.get("MODEL_NAME", "gpt-4o"),
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a code analysis assistant. "
                        "Classify the code difficulty as easy, medium, or hard. "
                        "Provide 2-3 suggestions. "
                        "Return JSON with keys difficulty and suggestions."
                    )
                },
                {
                    "role": "user",
                    "content": f"Analyze this code:\n\n{code}"
                }
            ],
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)

        return JSONResponse(content={
            "difficulty": result.get("difficulty", "unknown"),
            "suggestions": result.get("suggestions", [])
        })

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "difficulty": "unknown",
                "suggestions": [f"Analysis failed: {str(e)}"]
            }
        )
