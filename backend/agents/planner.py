from llm import get_llm
import json
import re

def planner_node(state):
    llm = get_llm()
    framework = state.get("framework", "fastapi")

    if framework == "nodejs":
        instruction = "list the JavaScript files needed to build it using Node.js and Express"
        example = '[{"filename": "server.js", "description": "Express app entrypoint with all routes registered"}, {"filename": "models.js", "description": "Data models"}]'
    else:
        instruction = "list the Python files needed to build it using FastAPI"
        example = '[{"filename": "main.py", "description": "FastAPI app entrypoint with all routes registered using @app.get/@app.post/@app.put/@app.delete"}, {"filename": "models.py", "description": "Pydantic models"}]'

    prompt = f"""You are a software architect. Given this backend project request, 
{instruction}.

Request: {state['task']}

Respond ONLY with a JSON array, nothing else — no numbered steps, no explanation, no markdown.
Do NOT describe a development process. ONLY list the actual files to create.

Example format:
{example}"""

    response = llm.invoke(prompt)
    match = re.search(r"\[.*\]", response, re.DOTALL)

    if match:
        try:
            plan = json.loads(match.group())
        except json.JSONDecodeError:
            plan = []
    else:
        plan = []

    # Safety net: if the model still failed to produce a real file plan, force a sensible default
    if not plan or not isinstance(plan, list):
        if framework == "nodejs":
            plan = [
                {"filename": "server.js", "description": "Express app entrypoint with all CRUD routes"},
                {"filename": "models.js", "description": "Data models"}
            ]
        else:
            plan = [
                {"filename": "main.py", "description": "FastAPI app entrypoint with all CRUD routes using @app decorators"},
                {"filename": "models.py", "description": "Pydantic models for request/response"}
            ]

    return {"plan": plan}