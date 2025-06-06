import json
import subprocess

PROMPT_TEMPLATE = """
You are an expert job matcher.

Given the following resume:
Name: {name}
Email: {email}
Phone: {phone}
Skills: {skills}
Experience: {experience}

And these job descriptions:
{jobs}

Rank the most suitable jobs from the list, provide a numeric match score between 0 and 100 for each job, and explain why.

Return your answer in JSON with:
- "best_matches": a list of objects, each with "title", "score", and "reason"
- The list should be sorted from highest to lowest score.
"""

def match_resume_with_jobs(resume_data, job_descriptions):
    prompt = PROMPT_TEMPLATE.format(
        name=resume_data.get("name", ""),
        email=resume_data.get("email", ""),
        phone=resume_data.get("phone", ""),
        skills=", ".join(resume_data.get("skills", [])),
        experience=resume_data.get("experience", ""),
        jobs=json.dumps(job_descriptions)
    )

    try:
        result = subprocess.run(
            ["ollama", "run", "llama3.2:3b", prompt],
            capture_output=True,
            text=True,
            timeout=180
        )
        raw_response = result.stdout.strip()

        start = raw_response.find("{")
        end = raw_response.rfind("}") + 1
        json_str = raw_response[start:end]
        parsed = json.loads(json_str)

        return {
            "raw_response": raw_response,
            "parsed_matches": parsed.get("best_matches", [])
        }

    except subprocess.TimeoutExpired:
        return {f"error": "Ollama command timed out after {timeout} seconds"}
    except json.JSONDecodeError:
        return {"error": "Failed to parse JSON from Ollama response", "raw_response": raw_response}
    except Exception as e:
        return {"error": str(e)}
