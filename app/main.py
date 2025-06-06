from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends, status
from fastapi.responses import JSONResponse, FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional
import os, uuid, json, pandas as pd

from app.services.llama_ollama import get_llama_response
from file_classifier import classify_file
from ocr.ocr_utils import extract_text_from_file
from parsers import parse_file_by_type, resume_parser
from job_maching.job_matcher import match_resume_to_jobs
from auth.service import AuthService
from auth.models import User
from middleware.auth import get_current_user
from database import get_db  # ← make sure you have this

app = FastAPI(title="OCR SaaS Platform", version="1.0.0")

TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

# ===================== /upload/ ===================== #
@app.post("/upload/")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Check subscription limits
        auth_service = AuthService()
        if not auth_service.check_document_limit(current_user):
            raise HTTPException(
                status_code=403,
                detail="Daily document limit exceeded. Please upgrade your subscription."
            )

        content = await file.read()
        extracted_text = extract_text_from_file(content, file.filename)
        doc_type = classify_file(extracted_text)
        parsed_data = parse_file_by_type(doc_type, extracted_text)

        # Use LLaMA for resume enhancement
        if doc_type == "resume":
            llm_prompt = f"Extract name, email, phone, skills, and experience from the following text:\n\n{extracted_text}"
            llm_data = get_llama_response(llm_prompt)
            parsed_data["llm_extracted"] = llm_data

        response = {
            "filename": file.filename,
            "content_type": file.content_type,
            "file_size": len(content),
            "document_type": doc_type,
            "parsed_data": parsed_data,
            "extracted_text_preview": extracted_text[:300]
        }

        # Save tabular data to CSV
        csv_path, df = None, None
        if doc_type == "marksheet" and 'subjects' in parsed_data:
            df = pd.DataFrame(list(parsed_data['subjects'].items()), columns=["Subject", "Marks"])
        elif doc_type in ["cheque", "lorry_challan"] and 'fields' in parsed_data:
            df = pd.DataFrame(list(parsed_data['fields'].items()), columns=["Field", "Value"])

        if df is not None:
            unique_csv_name = f"{uuid.uuid4().hex}_{file.filename}.csv"
            csv_path = os.path.join(TEMP_DIR, unique_csv_name)
            df.to_csv(csv_path, index=False)
            response["csv_download_url"] = f"/download_csv/?filename={unique_csv_name}"

        # Log processed document count
        current_user.documents_processed_today += 1
        db.commit()

        return JSONResponse(response)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process file: {str(e)}")


# ===================== /download_csv/ ===================== #
@app.get("/download_csv/")
async def download_csv(filename: str):
    csv_path = os.path.join(TEMP_DIR, filename)
    if os.path.exists(csv_path):
        return FileResponse(csv_path, media_type="text/csv", filename=filename)
    raise HTTPException(status_code=404, detail="CSV file not found.")


# ===================== /match_resume/ ===================== #
@app.post("/match_resume/")
async def match_resume(file: UploadFile = File(...), job_descriptions: str = Form(...)):
    content = await file.read()
    try:
        job_list = json.loads(job_descriptions)
        if not isinstance(job_list, list):
            raise ValueError
    except Exception:
        raise HTTPException(status_code=400, detail='Invalid job_descriptions. Must be a JSON list. Example: ["Job 1", "Job 2"]')

    extracted_text = extract_text_from_file(content, file.filename)
    doc_type = classify_file(extracted_text)

    if doc_type != "resume":
        raise HTTPException(status_code=400, detail="Uploaded file is not a resume.")

    parsed_resume = resume_parser.parse_resume(extracted_text)
    job_matches = match_resume_to_jobs(parsed_resume, job_list)

    return JSONResponse({
        "parsed_resume": parsed_resume,
        "job_matches": job_matches
    })


# ===================== /register/ ===================== #
@app.post("/register")
async def register(email: str, password: str, db: Session = Depends(get_db)):
    auth_service = AuthService()

    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = auth_service.get_password_hash(password)
    new_user = User(email=email, password_hash=hashed_password)
    db.add(new_user)
    db.commit()

    access_token = auth_service.create_access_token(data={"sub": str(new_user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


# ===================== /login/ ===================== #
@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    auth_service = AuthService()

    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not auth_service.verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    access_token = auth_service.create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}
