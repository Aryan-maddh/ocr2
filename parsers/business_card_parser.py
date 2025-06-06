import re

def parse_business_card(text: str) -> dict:
    data = {}

    # Extract email
    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    data['email'] = email_match.group() if email_match else ""

    # Extract phone number
    phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)*\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
    data['phone'] = phone_match.group() if phone_match else ""

    # Extract name (first line)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    data['name'] = lines[0] if lines else ""

    # Extract company name (try heuristic: line after name or containing "Inc", "Ltd", etc.)
    company = ""
    for i, line in enumerate(lines):
        if line == data['name'] and i+1 < len(lines):
            next_line = lines[i+1]
            if any(x in next_line.lower() for x in ['inc', 'ltd', 'company', 'corp']):
                company = next_line
                break
    data['company'] = company

    return data
