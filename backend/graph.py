from typing import TypedDict, Dict, List

class FileSpec(TypedDict):
    filename: str
    description: str

class AgentState(TypedDict):
    task: str
    framework: str
    plan: List[FileSpec]       # list of {filename, description}
    files: Dict[str, str]      # filename -> code content
    test_result: str
    passed: bool
    review: str
    approved: bool
    iteration: int
    project_dir: str