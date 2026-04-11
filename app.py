from fastapi import FastAPI, Request, Body
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import ast  # For syntax checking

from environment import CodeAnalysisEnv
from models import Action
from tasks import TASKS

app = FastAPI()
env = CodeAnalysisEnv()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def home(request: Request):
    state = env.state()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "state": state.model_dump()
        }
    )

@app.post("/reset")
async def reset(level: str = "easy"):
    result = env.reset(level)
    return JSONResponse(content=result.dict())


@app.post("/step")
async def step(action: Action):
    result = env.step(action)
    return JSONResponse(content=result.dict())


# --- Custom code analysis with syntax check ---
@app.post("/analyze")
async def analyze(data: dict = Body(...)):
    code = data.get("code", "")
    if not code.strip():
        return JSONResponse(content={"difficulty": "unknown", "suggestions": ["No code provided"]})

    # Step 1: Check Python syntax
    try:
        ast.parse(code)
        syntax_error = False
    except SyntaxError:
        syntax_error = True

    if syntax_error:
        return JSONResponse(content={
            "difficulty": "easy",
            "suggestions": [
                "Syntax error detected",
                "Check your code formatting and indentation"
            ]
        })

    # Step 2: Check against known TASKS
    for level, task in TASKS.items():
        if task["issue"] in code.lower() or task["code"].strip() in code.strip():
            difficulty = task["difficulty"]
            suggestions = [f"Detected issue similar to '{task['issue']}'"]
            break
    else:
        # Step 3: Fallback heuristic
        if "def " in code or "for " in code or "while " in code:
            difficulty = "medium"
            suggestions = ["Contains loops or functions, check runtime errors"]
        elif "SELECT" in code or "user_input" in code:
            difficulty = "hard"
            suggestions = ["Potential SQL or security issues"]
        else:
            difficulty = "easy"
            suggestions = ["Check for variable naming and code style"]

    return JSONResponse(content={"difficulty": difficulty, "suggestions": suggestions})