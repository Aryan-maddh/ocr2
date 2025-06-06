from .resume_parser import parse_resume
from .invoice_parser import parse_invoice
from .business_card_parser import parse_business_card
from .marksheet_parser import parse_marksheet
from .cheque_parser import parse_cheque
from .lorry_challan_parser import parse_lorry_challan
from .generic_parser import parse_generic

def parse_file_by_type(file_type, extracted_text):
    if file_type == "resume":
        return parse_resume(extracted_text)
    elif file_type == "invoice":
        return parse_invoice(extracted_text)
    elif file_type == "business_card":
        return parse_business_card(extracted_text)
    elif file_type == "marksheet":
        return parse_marksheet(extracted_text)
    elif file_type == "cheque":
        return parse_cheque(extracted_text)
    elif file_type == "lorry_challan":
        return parse_lorry_challan(extracted_text)
    else:
        return parse_generic(extracted_text)
