import requests

def get_llama_response(prompt: str, model: str = "llama3.2:3b"):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False}
        )
        response.raise_for_status()
        return response.json()["response"]
    except Exception as e:
        return f"LLM error: {str(e)}"
