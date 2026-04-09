from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from environment import CodeReviewEnv
from models import CodeReviewAction

app = FastAPI()
env = CodeReviewEnv()

@app.get("/health")
async def health():
    return {"status": "healthy", "environment": "code_review"}

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
