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


def debugger_node(state):
    llm = get_llm()
    files = state["files"]
    all_code = "\n\n".join(f"### FILE: {filename}\n{code}" for filename, code in files.items())
    feedback = state.get("test_result", "") + "\n" + state.get("review", "")

    import_requirement = (
        "IMPORT DISCIPLINE: Import FastAPI helpers directly from the top-level 'fastapi' package only — "
        "e.g. 'from fastapi import FastAPI, APIRouter, Depends, HTTPException, File, Form, UploadFile, Query, Path, Body, status'. "
        "NEVER import from submodules like fastapi.dependencies, fastapi.params, or fastapi.routing — these are internal and will break. "
        "For SQLAlchemy, use 'from sqlalchemy.orm import Session' and 'from sqlalchemy import Column, Integer, String, Float' as needed. "
        "IMPORTANT: pip package names with hyphens use underscores when imported in code — e.g. 'pip install pydantic-settings' but "
        "'from pydantic_settings import Settings'; 'pip install python-jose' but 'from jose import jwt'. "
        "Python identifiers cannot contain hyphens."
    )

    consistency_requirement = (
        "CROSS-FILE CONSISTENCY: If one file imports a name from another file (e.g. 'from routers import customer_router', "
        "'from database import get_db'), you MUST check that the exact name is actually defined in that source file. "
        "If it's missing, ADD the missing function/variable/router with that EXACT name — do not rename the import instead. "
        "This is the most common cause of failures: an import expects a name that was never created. "
        "Fix this by defining the missing name, not by changing the import."
    )

    prompt = f"""The following multi-file project failed testing or review. Fix all the files 
that need it, and output ALL files (even unchanged ones) in this exact format:

IMPORTANT: All files will be in the SAME folder. Use plain imports like 
"from todo_item import TodoItem" — NEVER use relative imports like 
"from .todo_item import TodoItem" or "from . import todo_item".
Do NOT create test files or use pytest — testing is handled externally. 
If a test_api.py file exists, remove it entirely.
{import_requirement}
{consistency_requirement}

### FILE: <filename>
<code for that file>

Project files:
{all_code}

Feedback:
{feedback}

Do not include any text outside this format."""

    response = llm.invoke(prompt)

    fixed_files = {}
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
        fixed_files[filename] = code

    iteration = state.get("iteration", 0) + 1
    return {"files": fixed_files, "iteration": iteration}

    