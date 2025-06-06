import re

def parse_resume(text: str) -> dict:
    data = {}

    # Extract email
    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    data['email'] = email_match.group() if email_match else ""

    # Extract phone number
    phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)*\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
    data['phone'] = phone_match.group() if phone_match else ""

    # Extract name (first non-empty line)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    data['name'] = lines[0] if lines else ""

    # Extract skills section
    skills = []
    skills_section = re.search(r'Skills[:\n](.*?)(?:Experience|Education|$)', text, re.DOTALL | re.IGNORECASE)
    if skills_section:
        skills_text = skills_section.group(1)
        skills = [s.strip() for s in re.split(r'[,;\n]', skills_text) if s.strip()]
    data['skills'] = skills

    return data
