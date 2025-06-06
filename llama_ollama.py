import json
import re
import subprocess

def get_llama_response(prompt: str, model: str = "llama3.2:3b"):
    try:
        command = ["ollama", "run", model, prompt]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=180)  # increased to 3 minutes

        if result.returncode != 0:
            raise RuntimeError(result.stderr)

        return parse_response(result.stdout)
    except Exception as e:
        return {"error": str(e)}

def parse_response(raw_output: str):
    # Basic attempt to parse JSON from LLM response
    try:
        return json.loads(raw_output)
    except json.JSONDecodeError:
        return {"raw_response": raw_output}

def parse_llama_response(raw_text):
    # Use regex to extract JSON inside triple backticks (```json ... ```)
    json_match = re.search(r"```json(.*?)```", raw_text, re.DOTALL)
    if json_match:
        json_str = json_match.group(1).strip()
        try:
            data = json.loads(json_str)
            return data
        except json.JSONDecodeError:
            # Failed to parse JSON, return raw text as fallback
            return {"raw_response": raw_text}
    else:
        # No JSON found, return raw text
        return {"raw_response": raw_text}

# Example usage after getting raw response from subprocess:
def get_job_match_from_llama(prompt: str):
    raw_response = call_ollama_subprocess(prompt)
    parsed = parse_llama_response(raw_response)
    return parsed
