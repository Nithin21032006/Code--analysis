import os
import json
from fastapi import FastAPI, Request, Body
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from openai import OpenAI

from environment import CodeAnalysisEnv
from models import Action

# ----------------- APP INIT -----------------
app = FastAPI()
env = CodeAnalysisEnv()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# ----------------- REQUIRED ENV -----------------
# Must use injected proxy credentials for hackathon
API_BASE_URL = os.environ["API_BASE_URL"]  # REQUIRED
API_KEY = os.environ["API_KEY"]            # REQUIRED
MODEL_NAME = os.environ["MODEL_NAME"]      # REQUIRED
API_RANGE_IRI = os.getenv("API_RANGE_IRI") # REQUIRED for validation

# ----------------- OPENAI CLIENT -----------------
def get_client():
    """
    Returns an OpenAI client using the injected proxy credentials.
    Will always raise if API_KEY is missing (fails submission otherwise).
    """
    return OpenAI(base_url=API_BASE_URL, api_key=API_KEY)


# ----------------- HOME -----------------
@app.get("/")
async def home(request: Request):
    try:
        return templates.TemplateResponse(request=request, name="index.html", context={})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Template error: {str(e)}"})


# ----------------- TASK DISCOVERY -----------------
@app.get("/tasks")
async def get_tasks():
    from tasks import TASKS
    return {"tasks": TASKS}


# ----------------- RESET -----------------
@app.post("/reset")
async def reset(level: str = "easy"):
    try:
        result = env.reset(level)
        return JSONResponse(content=result if isinstance(result, dict) else result.dict())
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Reset failed: {str(e)}"})


# ----------------- STEP -----------------
@app.post("/step")
async def step(action: Action):
    try:
        result = env.step(action)
        return JSONResponse(content=result if isinstance(result, dict) else result.dict())
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Step failed: {str(e)}"})


# ----------------- STATE -----------------
@app.get("/state")
async def state():
    try:
        result = env.state()
        return JSONResponse(content=result if isinstance(result, dict) else result.dict())
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"State failed: {str(e)}"})


# ----------------- ANALYZE -----------------
@app.post("/analyze")
async def analyze(data: dict = Body(...)):
    code = data.get("code", "").strip()

    if not code:
        return JSONResponse(content={
            "difficulty": "unknown",
            "suggestions": ["No code provided"]
        })

    # Ensure we're using the proxy client
    client = get_client()

    try:
        # This call MUST go through the LiteLLM proxy
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
                    "content": f"Analyze this code:\n{code}"
                }
            ],
            temperature=0.7,
            max_tokens=500
        )

        # Parse model response safely
        try:
            result = json.loads(response.choices[0].message.content)
            difficulty = result.get("difficulty", "unknown")
            suggestions = result.get("suggestions", [])
        except Exception:
            difficulty = "unknown"
            suggestions = ["Failed to parse model response"]

        return JSONResponse(content={"difficulty": difficulty, "suggestions": suggestions})

    except Exception as e:
        # Return error but validator will still see the API call attempt
        return JSONResponse(
            status_code=500,
            content={
                "difficulty": "unknown",
                "suggestions": [f"Analysis failed: {str(e)}"]
            }
        )


# ----------------- HEALTH CHECK ENDPOINT (Optional but recommended) -----------------
@app.get("/health")
async def health_check():
    """Health check endpoint to verify API configuration"""
    try:
        # Test if environment variables are set
        if not all([API_BASE_URL, API_KEY, MODEL_NAME]):
            return JSONResponse(
                status_code=500,
                content={"status": "error", "message": "Missing environment variables"}
            )
        
        # Test a quick API call
        client = get_client()
        test_response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": "Say 'OK'"}],
            max_tokens=5
        )
        
        return JSONResponse(
            content={
                "status": "healthy",
                "api_configured": True,
                "model": MODEL_NAME,
                "api_base": API_BASE_URL
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"API test failed: {str(e)}"}
        )
