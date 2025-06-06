import os
import tempfile
from paddleocr import PaddleOCR
from pdf2image import convert_from_bytes
import fitz  # PyMuPDF

ocr_model = PaddleOCR(use_angle_cls=True, lang='en')

def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    ext = filename.lower().split('.')[-1]

    if ext in ['jpg', 'jpeg', 'png']:
        return ocr_image_bytes(file_bytes)

    elif ext == 'pdf':
        # Try direct text extraction
        text = extract_text_from_pdf(file_bytes)
        if not text.strip():
            # fallback to OCR
            return ocr_pdf_as_image(file_bytes)
        return text

    else:
        raise ValueError("Unsupported file format")


def ocr_image_bytes(file_bytes: bytes) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        result = ocr_model.ocr(tmp_path)
        text = '\n'.join([line[1][0] for line in result[0]]) if result else ""
        return text
    finally:
        os.remove(tmp_path)


def ocr_pdf_as_image(file_bytes: bytes) -> str:
    images = convert_from_bytes(file_bytes)
    full_text = ""
    for img in images:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            img.save(tmp.name, format='PNG')
            result = ocr_model.ocr(tmp.name)
            text = '\n'.join([line[1][0] for line in result[0]]) if result else ""
            full_text += text + "\n"
            os.remove(tmp.name)
    return full_text


def extract_text_from_pdf(file_bytes: bytes) -> str:
    try:
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            text = ""
            for page in doc:
                text += page.get_text()
        return text
    except Exception:
        return ""
