import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io

async def extract_text(file):
    content = await file.read()
    if file.filename.endswith(".pdf"):
        pdf = fitz.open(stream=content, filetype="pdf")
        text = "\n".join(page.get_text() for page in pdf)
    else:
        img = Image.open(io.BytesIO(content))
        text = pytesseract.image_to_string(img)
    return text.strip()
