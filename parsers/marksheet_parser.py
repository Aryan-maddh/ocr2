import re

def parse_marksheet(text: str) -> dict:
    data = {}

    name_match = re.search(r'Name\s*[:\-]?\s*(.+)', text, re.IGNORECASE)
    data['name'] = name_match.group(1).strip() if name_match else ""

    roll_match = re.search(r'Roll\s*No\.?\s*[:\-]?\s*(\w+)', text, re.IGNORECASE)
    data['roll_no'] = roll_match.group(1).strip() if roll_match else ""

    subjects = {}
    for match in re.finditer(r'([A-Za-z\s]+)\s+(\d{1,3})', text):
        subject = match.group(1).strip()
        marks = int(match.group(2))
        if len(subject) > 2 and marks <= 100:
            subjects[subject] = marks
    data['subjects'] = subjects

    total_match = re.search(r'Total\s*[:\-]?\s*(\d+)', text, re.IGNORECASE)
    data['total'] = int(total_match.group(1)) if total_match else None

    perc_match = re.search(r'Percentage\s*[:\-]?\s*([\d\.]+)', text, re.IGNORECASE)
    data['percentage'] = float(perc_match.group(1)) if perc_match else None

    return data
