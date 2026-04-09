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
- 0.01-0.99 scoring range

### Medium: Logic & Performance Review
- Detect off-by-one errors, edge cases, inefficiencies
- Bonus for fix suggestions

### Hard: Security & Architecture Review
- SQL injection, XSS, authentication flaws
- Critical severity gets higher rewards

## Setup

```bash
docker build -t code-review-env .
docker run -p 7860:7860 code-review-env
