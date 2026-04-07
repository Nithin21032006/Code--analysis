import os
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

# ✅ Use injected proxy credentials — do NOT hardcode these
client = OpenAI(
    base_url=os.environ["API_BASE_URL"],
    api_key=os.environ["API_KEY"],
)


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


@app.post("/analyze")
async def analyze(data: dict = Body(...)):
    code = data.get("code", "")
    if not code.strip():
        return JSONResponse(content={"difficulty": "unknown", "suggestions": ["No code provided"]})

    # ✅ Call LLM through the proxy
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a code analysis assistant. Given a code snippet, "
                    "identify its difficulty (easy, medium, or hard) and provide "
                    "2-3 concrete suggestions to improve or fix it. "
                    "Reply in JSON with keys: difficulty (string), suggestions (list of strings)."
                )
            },
            {
                "role": "user",
                "content": f"Analyze this code:\n\n```\n{code}\n```"
            }
        ],
        response_format={"type": "json_object"},
    )

    import json
    result = json.loads(response.choices[0].message.content)
    return JSONResponse(content={
        "difficulty": result.get("difficulty", "unknown"),
        "suggestions": result.get("suggestions", [])
    })