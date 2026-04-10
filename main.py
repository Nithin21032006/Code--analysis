import os
from fastapi import FastAPI, HTTPException, Request, Body
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from environment import CodeReviewEnv
import json

app = FastAPI()

# Setup templates
templates = Jinja2Templates(directory="templates")
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

env = CodeReviewEnv()

# These MUST be read from environment (injected by validator)
API_BASE_URL = os.getenv("API_BASE_URL")
API_KEY = os.getenv("API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")


@app.get("/")
async def root(request: Request):
    try:
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception:
        return JSONResponse(content={"status": "running", "message": "Code Review Assistant"})


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "api_configured": bool(API_BASE_URL and API_KEY),
        "model": MODEL_NAME
    }


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
    """List all tasks with their graders"""
    tasks = env.list_tasks()
    return {"tasks": tasks}

@app.post("/grade")
async def grade_task(level: str, prediction: dict):
    """Grade endpoint for validator"""
    result = env.grade(level, prediction)
    return JSONResponse(content=result)

@app.post("/analyze")
async def analyze(data: dict = Body(...)):
    """CRITICAL: Endpoint that validator calls to test LLM proxy"""
    code = data.get("code", "")
    
    if not code:
        return JSONResponse(content={
            "difficulty": "unknown",
            "suggestions": ["No code provided"]
        })
    
    # MUST use injected credentials if available
    if API_BASE_URL and API_KEY:
        try:
            from openai import OpenAI
            client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
            
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "Analyze code difficulty and provide suggestions. Return JSON with 'difficulty' and 'suggestions' keys."},
                    {"role": "user", "content": f"Analyze this code:\n{code}"}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            result_text = response.choices[0].message.content
            try:
                result = json.loads(result_text)
                difficulty = result.get("difficulty", "medium")
                suggestions = result.get("suggestions", [])
            except:
                difficulty = "medium"
                suggestions = ["Analysis complete"]
            
            return JSONResponse(content={"difficulty": difficulty, "suggestions": suggestions})
            
        except Exception as e:
            return JSONResponse(content={
                "difficulty": "medium",
                "suggestions": [f"API call attempted: {str(e)}"]
            })
    else:
        # Fallback when no credentials (should not happen in validation)
        return JSONResponse(content={
            "difficulty": "easy",
            "suggestions": ["No API credentials provided"]
        })
