from fastapi import FastAPI, Request, Body
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from environment import CodeAnalysisEnv
from models import Action

app = FastAPI()
env = CodeAnalysisEnv()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def home(request: Request):
    state = env.state()
    return templates.TemplateResponse("index.html", {"request": request, "state": state.dict()})


@app.post("/reset")
async def reset(level: str = "easy"):
    result = env.reset(level)
    return JSONResponse(content=result.dict())


@app.post("/step")
async def step(action: Action):
    result = env.step(action)
    return JSONResponse(content=result.dict())


# --- Custom code analysis ---
@app.post("/analyze")
async def analyze(data: dict = Body(...)):
    code = data.get("code", "")
    if not code.strip():
        return JSONResponse(content={"difficulty": "unknown", "suggestions": ["No code provided"]})

    # Simple heuristic / AI logic (can extend later)
    if "print(" in code or "def " in code:
        difficulty = "easy"
        suggestions = ["Check for syntax errors", "Use meaningful variable names"]
    elif "for " in code or "while " in code:
        difficulty = "medium"
        suggestions = ["Check for index out of range", "Add error handling for loops"]
    else:
        difficulty = "hard"
        suggestions = ["Check for security issues", "Validate all user inputs"]

    return JSONResponse(content={"difficulty": difficulty, "suggestions": suggestions})