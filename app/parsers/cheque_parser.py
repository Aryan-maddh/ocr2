import re

def parse_cheque(text: str) -> dict:
    # Extract cheque fields like payee name, amount, date, bank
    data = {}

    payee = re.search(r'Pay\s*to\s*the\s*Order\s*of\s*:?(.+)', text, re.IGNORECASE)
    data['payee'] = payee.group(1).strip() if payee else ""

    amount = re.search(r'Rs\.?\s*([\d,]+\.?\d*)', text, re.IGNORECASE)
    data['amount'] = amount.group(1).strip() if amount else ""

    date = re.search(r'Date\s*[:\-]?\s*([\d/]+)', text, re.IGNORECASE)
    data['date'] = date.group(1).strip() if date else ""

    bank = re.search(r'Bank\s*[:\-]?\s*(.+)', text, re.IGNORECASE)
    data['bank'] = bank.group(1).strip() if bank else ""

    data['fields'] = data.copy()  # for CSV export convenience

    return data
