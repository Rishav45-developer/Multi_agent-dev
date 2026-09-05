from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langgraph.graph import StateGraph, END
from graph import AgentState
from agents.planner import planner_node
from agents.coder import coder_node
from agents.tester import tester_node
from agents.reviewer import reviewer_node
from agents.debugger import debugger_node
from zip_utils import create_zip_from_files
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_ITERATIONS = 3

# Simple in-memory store: task_id -> result
task_store = {}

def route_after_test(state):
    if state["passed"] and state.get("iteration", 0) < MAX_ITERATIONS:
        return "reviewer"
    if state.get("iteration", 0) >= MAX_ITERATIONS:
        return END
    return "debugger"

def route_after_review(state):
    if state["approved"]:
        return END
    if state.get("iteration", 0) >= MAX_ITERATIONS:
        return END
    return "debugger"

workflow = StateGraph(AgentState)
workflow.add_node("planner", planner_node)
workflow.add_node("coder", coder_node)
workflow.add_node("tester", tester_node)
workflow.add_node("reviewer", reviewer_node)
workflow.add_node("debugger", debugger_node)

workflow.set_entry_point("planner")
workflow.add_edge("planner", "coder")
workflow.add_edge("coder", "tester")
workflow.add_conditional_edges("tester", route_after_test)
workflow.add_conditional_edges("reviewer", route_after_review)
workflow.add_edge("debugger", "tester")

app_graph = workflow.compile()

class TaskRequest(BaseModel):
    task: str
    framework: str = "fastapi"

@app.post("/generate")
def generate(req: TaskRequest):
    result = app_graph.invoke({
        "task": req.task,
        "framework": req.framework,
        "iteration": 0
    })

    task_id = str(uuid.uuid4())
    task_store[task_id] = result

    result["task_id"] = task_id
    return result

@app.get("/download/{task_id}")
def download(task_id: str):
    if task_id not in task_store:
        raise HTTPException(status_code=404, detail="Task not found")

    files = task_store[task_id]["files"]
    zip_bytes = create_zip_from_files(files)

    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=project_{task_id}.zip"}
    )