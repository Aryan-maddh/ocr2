import requests
import json
import subprocess
from typing import Dict, List, Optional
import openai  # For potential future API integration

class EnhancedLLMService:
    def __init__(self, model_name: str = "llama3.2:3b"):
        self.model_name = model_name
        self.use_ollama = True
    
    def get_structured_response(self, prompt: str, max_retries: int = 3) -> Dict:
        """Get structured JSON response from LLM with retry logic"""
        for attempt in range(max_retries):
            try:
                if self.use_ollama:
                    result = self._call_ollama(prompt)
                else:
                    result = self._call_openai_api(prompt)
                
                # Try to parse JSON
                if isinstance(result, str):
                    # Extract JSON from response
                    json_start = result.find('{')
                    json_end = result.rfind('}') + 1
                    if json_start != -1 and json_end != 0:
                        json_str = result[json_start:json_end]
                        return json.loads(json_str)
                
                return result if isinstance(result, dict) else {"raw_response": result}
                
            except Exception as e:
                if attempt == max_retries - 1:
                    return {"error": f"Failed after {max_retries} attempts: {str(e)}"}
                continue
    
    def _call_ollama(self, prompt: str) -> str:
        """Call Ollama locally"""
        try:
            result = subprocess.run(
                ["ollama", "run", self.model_name, prompt],
                capture_output=True,
                text=True,
                timeout=180
            )
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            raise Exception("Ollama request timed out")
        except Exception as e:
            raise Exception(f"Ollama error: {str(e)}")
    
    def _call_openai_api(self, prompt: str) -> Dict:
        """Alternative: Call OpenAI API (for production use)"""
        # Implementation for OpenAI API calls
        pass
    
    def optimize_for_document_type(self, document_type: str) -> str:
        """Get optimized prompt prefix for specific document types"""
        prefixes = {
            "resume": "You are an expert HR professional analyzing resumes.",
            "invoice": "You are an expert accountant analyzing invoices.",
            "marksheet": "You are an expert academic administrator analyzing academic transcripts.",
            "business_card": "You are an expert in business networking analyzing business cards.",
            "cheque": "You are an expert banking professional analyzing cheques.",
            "lorry_challan": "You are an expert logistics professional analyzing transport documents."
        }
        return prefixes.get(document_type, "You are an expert document analyzer.")

# Enhanced API endpoints
@app.post("/process_custom_fields/")
async def process_custom_fields(
    document_id: str,
    custom_fields: List[str],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Extract additional custom fields from a processed document"""
    processor = DocumentProcessor()
    
    # Get document
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Get original text (you'd need to store this or re-extract)
    extracted_text = processor.ocr_service.extract_text_from_file(
        document.file_path, document.filename
    )
    
    # Extract custom fields
    custom_data = processor.extract_custom_fields(
        extracted_text, document.document_type, custom_fields
    )
    
    # Store custom extracted data
    for field_name, field_info in custom_data.items():
        if field_info and field_info.get('value'):
            existing_data = db.query(ExtractedData).filter(
                ExtractedData.document_id == document_id,
                ExtractedData.field_name == field_name
            ).first()
            
            if existing_data:
                existing_data.field_value = str(field_info['value'])
                existing_data.confidence_score = field_info.get('confidence', 0.8)
            else:
                new_data = ExtractedData(
                    document_id=document_id,
                    field_name=field_name,
                    field_value=str(field_info['value']),
                    confidence_score=field_info.get('confidence', 0.8)
                )
                db.add(new_data)
    
    db.commit()
    return {"message": "Custom fields extracted successfully", "data": custom_data}

@app.get("/field_suggestions/{document_id}")
async def get_field_suggestions(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get suggested additional fields for a document"""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    suggestions = json.loads(document.suggested_fields or "[]")
    return {"suggestions": suggestions}


def query_llama(prompt: str) -> str:
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama3:3b", "prompt": prompt, "stream": False}
        )
        response.raise_for_status()
        result = response.json()
        return result.get("response", "").strip()
    except Exception as e:
        return f"LLM error: {str(e)}"
