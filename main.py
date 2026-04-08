mport os
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


# ---------------- SAFE CONFIG ----------------
API_BASE_URL = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
API_KEY = os.environ.get("API_KEY") or os.environ.get("HF_TOKEN")
MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-4o-mini")


def get_client():
    """
    Create OpenAI client only when needed.
    Prevents startup crash if API key is missing.
    """
    if not API_KEY:
        return None

    return OpenAI(
        base_url=API_BASE_URL,
        api_key=API_KEY
    )


# ---------------- HOME ----------------
@app.get("/")
async def home(request: Request):
    try:
        return templates.TemplateResponse(
            "index.html",
            {"request": request}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Template error: {str(e)}"}
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
        return JSONResponse(content=result if isinstance(result, dict) else result.dict())
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
        return JSONResponse(content=result if isinstance(result, dict) else result.dict())
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
        return JSONResponse(content=result if isinstance(result, dict) else result.dict())
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"State failed: {str(e)}"}
        )


# ---------------- ANALYZE ----------------
@app.post("/analyze")
async def analyze(data: dict = Body(...)):
    code = data.get("code", "").strip()

    if not code:
        return JSONResponse(content={
            "difficulty": "unknown",
            "suggestions": ["No code provided"]
        })

    client = get_client()

    # fallback if no API key
    if client is None:
        return JSONResponse(content={
            "difficulty": "medium",
            "suggestions": [
                "API key not configured",
                "Using fallback local analysis",
                "Check syntax and logic manually"
            ]
        })

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
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
