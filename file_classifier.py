def classify_file(text: str) -> str:
    text = text.lower()

    if "experience" in text and ("education" in text or "skills" in text or "projects" in text):
        return "resume"
    elif "invoice number" in text or "amount due" in text or "gstin" in text:
        return "invoice"
    elif "marks" in text and ("subject" in text or "grade" in text):
        return "marksheet"
    elif "cheque no" in text or "pay to" in text:
        return "cheque"
    elif "challan" in text or "lorry" in text:
        return "lorry_challan"
    elif "mobile" in text and "email" in text:
        return "business_card"
    else:
        return "generic"
