# Code Analysis OpenEnv

This environment evaluates AI agents on code analysis tasks.

## Levels
- Easy → Syntax error detection
- Medium → Runtime bug detection
- Hard → Security vulnerability detection

## API
- POST /reset
- POST /step
- GET /state

## Run
uvicorn app:app --reload