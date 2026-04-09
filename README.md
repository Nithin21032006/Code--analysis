---
title: Code Review Assistant
emoji: 🔍
colorFrom: blue
colorTo: indigo
sdk: docker
sdk_version: "1.0"
app_file: main.py
pinned: false
---

# Code Review Assistant Environment

A realistic OpenEnv environment where AI agents learn to review code, identify issues, and suggest fixes.

## Real-World Utility

Code review is a daily task for software engineers. This environment trains agents to:
- Find syntax errors and style violations
- Detect logic bugs and performance issues  
- Identify security vulnerabilities
- Provide constructive feedback

## Tasks

### Easy: Syntax & Style Review
- Find missing colons, imports, PEP 8 violations
- Score range: 0.01-0.99 (strictly between 0 and 1)

### Medium: Logic & Performance Review
- Detect off-by-one errors, edge cases, inefficiencies
- Bonus points for fix suggestions

### Hard: Security & Architecture Review
- SQL injection, XSS, authentication flaws
- Critical severity issues give higher rewards

## Setup Instructions

### Local Development

```bash
# Clone the repository
git clone https://github.com/Nithin21032006/Code--analysis
cd Code--analysis

# Install dependencies
pip install -r requirements.txt

# Run the FastAPI server
uvicorn main:app --reload --port 7860
