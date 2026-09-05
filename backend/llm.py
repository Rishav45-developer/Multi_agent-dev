from langchain_community.llms import Ollama
def get_llm(model: str = "qwen2.5-coder:3b"):
    return Ollama(model=model, temperature=0.2)

