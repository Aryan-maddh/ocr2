import re

def parse_invoice(text: str) -> dict:
    data = {}

    # Invoice Number
    invoice_no = re.search(r'(invoice number|inv\.? no\.?)[:\s]*([A-Za-z0-9\-]+)', text, re.IGNORECASE)
    data['invoice_number'] = invoice_no.group(2) if invoice_no else ""

    # Invoice Date
    date = re.search(r'(date)[:\s]*([\d/\-]{6,10})', text, re.IGNORECASE)
    data['date'] = date.group(2) if date else ""

    # Total Amount
    total = re.search(r'(total amount|amount due|total)[:\s]*([\d,\.]+)', text, re.IGNORECASE)
    data['total_amount'] = total.group(2) if total else ""

    # Vendor Name (example heuristic: line with "From" or "Vendor")
    vendor = re.search(r'(from|vendor)[:\s]*(.+)', text, re.IGNORECASE)
    data['vendor'] = vendor.group(2).strip() if vendor else ""

    return data
