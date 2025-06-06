from fastapi import APIRouter, File, UploadFile
from app.services.ocr_service import extract_text
from app.services.llama_service import query_llama

router = APIRouter()

@router.post("/process")
async def process_document(file: UploadFile = File(...)):
    text = await extract_text(file)
    refined_data = query_llama(f"Extract structured data from this text:\n\n{text}")
    return {"raw_text": text, "structured_data": refined_data}
