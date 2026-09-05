import re
from llm import get_llm


def ensure_fastapi_imports(code, filename):
    if not filename.endswith('.py'):
        return code
    needed = []
    check_names = ['Depends', 'HTTPException', 'status', 'File', 'Form', 'UploadFile', 'Query', 'Path', 'Body', 'APIRouter', 'FastAPI']
    for name in check_names:
        used = f'{name}(' in code or f': {name}' in code or f'-> {name}' in code
        already_imported = re.search(rf'\bimport\b[^\n]*\b{name}\b', code) is not None
        if used and not already_imported:
            needed.append(name)
    if needed:
        import_line = f"from fastapi import {', '.join(needed)}\n"
        code = import_line + code
    return code


def coder_node(state):
    llm = get_llm()
    framework = state.get("framework", "fastapi")
    lang = "JavaScript (Node.js/Express)" if framework == "nodejs" else "Python (FastAPI)"
    plan = state["plan"]

    file_list = "\n".join(f"- {f['filename']}: {f['description']}" if isinstance(f, dict) else f"- {f}" for f in plan)

    framework_requirement = (
        "You MUST use Express with actual routes like app.get('/todos', ...), app.post(...), etc."
        if framework == "nodejs" else
        "You MUST use FastAPI with actual HTTP route decorators like @app.get('/todos'), @app.post('/todos'), @app.put('/todos/{id}'), @app.delete('/todos/{id}'). This must be a real HTTP API, not a plain Python class or script."
    )

    import_requirement = (
        "IMPORT DISCIPLINE: Import FastAPI helpers directly from the top-level 'fastapi' package only — "
        "e.g. 'from fastapi import FastAPI, APIRouter, Depends, HTTPException, File, Form, UploadFile, Query, Path, Body, status'. "
        "NEVER import from submodules like fastapi.dependencies, fastapi.params, or fastapi.routing — these are internal and will break. "
        "For SQLAlchemy, use 'from sqlalchemy.orm import Session' and 'from sqlalchemy import Column, Integer, String, Float' as needed. "
        "IMPORTANT: pip package names with hyphens use underscores when imported in code — e.g. 'pip install pydantic-settings' but "
        "'from pydantic_settings import Settings'; 'pip install python-jose' but 'from jose import jwt'. "
        "Python identifiers cannot contain hyphens. Double-check every import path before finishing."
    )

    consistency_requirement = (
        "CONSISTENCY REQUIREMENT: Pick ONE concrete resource name and field set and use the EXACT same names for it in every file. "
        "Do not rename fields or the model between files. "
        "CROSS-FILE CONSISTENCY: If one file imports a function or variable from another file (e.g. 'from database import get_db'), "
        "you MUST actually define that exact function/variable with that exact name in the source file. "
        "Before finishing, verify every cross-file import actually exists in the file it's imported from."
    )

    prompt = f"""You are writing a complete {lang} backend project with these files:
{file_list}

Task: {state['task']}

CRITICAL REQUIREMENT: {framework_requirement}
{import_requirement}
{consistency_requirement}

IMPORTANT: All files will be in the SAME folder. Use plain imports like 
"from todo_item import TodoItem" — NEVER use relative imports like 
"from .todo_item import TodoItem" or "from . import todo_item".
Do NOT create test files or use pytest — testing is handled externally.

For EACH file, output it in exactly this format, with no extra explanation:

### FILE: <filename>
<code for that file>

Repeat this for every file. Do not include any text outside this format."""

    response = llm.invoke(prompt)

    files = {}
    parts = response.split("### FILE:")
    for part in parts[1:]:
        lines = part.strip().split("\n", 1)
        filename = lines[0].strip()
        code = lines[1].strip() if len(lines) > 1 else ""
        code = code.replace("```python", "").replace("```javascript", "").replace("```", "").strip()
        code = re.sub(r'from\s+\.(\w+)', r'from \1', code)
        code = re.sub(r'from\s+\.\s+import', 'from ', code)
        code = re.sub(r'from fastapi\.dependencies import', 'from fastapi import', code)
        code = re.sub(r'from fastapi\.params import', 'from fastapi import', code)
        code = re.sub(r'from\s+pydantic-settings\s+import', 'from pydantic_settings import', code)
        code = re.sub(r'import\s+pydantic-settings', 'import pydantic_settings', code)
        code = ensure_fastapi_imports(code, filename)
        files[filename] = code

    return {"files": files}