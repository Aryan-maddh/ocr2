import re

def parse_lorry_challan(text: str) -> dict:
    data = {}

    consignor = re.search(r'Consignor\s*[:\-]?\s*(.+)', text, re.IGNORECASE)
    data['consignor'] = consignor.group(1).strip() if consignor else ""

    consignee = re.search(r'Consignee\s*[:\-]?\s*(.+)', text, re.IGNORECASE)
    data['consignee'] = consignee.group(1).strip() if consignee else ""

    freight = re.search(r'Freight\s*[:\-]?\s*([\d,\.]+)', text, re.IGNORECASE)
    data['freight'] = freight.group(1).strip() if freight else ""

    data['fields'] = data.copy()

    return data
