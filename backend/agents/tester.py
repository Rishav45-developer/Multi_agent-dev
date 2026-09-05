import subprocess
import tempfile
import os
import sys

def tester_node(state):
    framework = state.get("framework", "fastapi")
    project_dir = tempfile.mkdtemp(prefix="genproj_")

    for filename, code in state["files"].items():
        filepath = os.path.join(project_dir, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            f.write(code)

    errors = []

    if framework == "nodejs":
        for filename in state["files"]:
            result = subprocess.run(
                ["node", "--check", filename],
                capture_output=True, text=True, timeout=10, cwd=project_dir
            )
            if result.returncode != 0:
                errors.append(f"{filename}: {result.stderr.strip()}")
    else:
        for filename in state["files"]:
            module_name = filename.replace(".py", "").replace("/", ".")
            result = subprocess.run(
                [sys.executable, "-c", f"import {module_name}"],
                capture_output=True, text=True, timeout=10, cwd=project_dir
            )
            if result.returncode != 0:
                errors.append(f"{filename}: {result.stderr.strip()}")

    passed = len(errors) == 0
    output = "All files checked successfully." if passed else "\n".join(errors)
    return {"test_result": output, "passed": passed, "project_dir": project_dir}