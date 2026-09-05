from llm import get_llm

def reviewer_node(state):
    llm = get_llm()
    files = state["files"]
    all_code = "\n\n".join(f"# {filename}\n{code}" for filename, code in files.items())

    prompt = f"""You are a code reviewer. Check this multi-file project for bugs, bad style, 
or logic errors. If everything looks correct, respond with exactly: APPROVED
Otherwise, respond with exactly: NEEDS_FIX followed by a short explanation.

Project files:
{all_code}"""
    review = llm.invoke(prompt)
    approved = review.strip().startswith("APPROVED")
    return {"review": review, "approved": approved}