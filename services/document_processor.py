import asyncio
from typing import Dict, List, Optional
import json
from celery import Celery
from sqlalchemy.orm import Session
from models.document import Document, ExtractedData
from services.llm_service import EnhancedLLMService
from services.ocr_service import EnhancedOCRService
from services.storage_service import StorageService

# Celery for background processing
celery_app = Celery('ocr_processor', broker='redis://localhost:6379')

class DocumentProcessor:
    def __init__(self):
        self.ocr_service = EnhancedOCRService()
        self.llm_service = EnhancedLLMService()
        self.storage_service = StorageService()
    
    async def process_document_async(self, document_id: str, user_id: str):
        """Queue document for background processing"""
        process_document_task.delay(document_id, user_id)
        return {"status": "queued", "document_id": document_id}
    
    def extract_custom_fields(self, text: str, document_type: str, custom_fields: List[str]) -> Dict:
        """Extract custom user-defined fields using LLM"""
        prompt = f"""
        Extract the following specific fields from this {document_type} document:
        
        Fields to extract: {', '.join(custom_fields)}
        
        Document text:
        {text}
        
        Return JSON with field names as keys and extracted values as values.
        If a field is not found, set value to null.
        Include confidence score (0-1) for each field.
        
        Format:
        {{
            "field_name": {{"value": "extracted_value", "confidence": 0.85}},
            ...
        }}
        """
        
        result = self.llm_service.get_structured_response(prompt)
        return result
    
    def get_field_suggestions(self, document_type: str, extracted_text: str) -> List[str]:
        """Suggest additional fields that could be extracted"""
        prompt = f"""
        Analyze this {document_type} and suggest 10 additional fields that could be extracted:
        
        {extracted_text[:500]}...
        
        Return only a JSON list of field names:
        ["field1", "field2", ...]
        """
        
        suggestions = self.llm_service.get_structured_response(prompt)
        return suggestions if isinstance(suggestions, list) else []

@celery_app.task
def process_document_task(document_id: str, user_id: str):
    """Background task for document processing"""
    processor = DocumentProcessor()
    db = SessionLocal()
    
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return {"error": "Document not found"}
        
        # Update status
        document.status = "processing"
        db.commit()
        
        # Extract text
        extracted_text = processor.ocr_service.extract_text_from_file(
            document.file_path, document.filename
        )
        
        # Classify document
        doc_type = processor.classify_document(extracted_text)
        document.document_type = doc_type
        
        # Extract standard fields
        parsed_data = processor.parse_document_by_type(doc_type, extracted_text)
        
        # Store extracted data
        for field_name, field_value in parsed_data.items():
            if field_value:  # Only store non-empty values
                extracted_data = ExtractedData(
                    document_id=document_id,
                    field_name=field_name,
                    field_value=str(field_value),
                    confidence_score=0.9  # Default confidence
                )
                db.add(extracted_data)
        
        # Get field suggestions for user
        suggestions = processor.get_field_suggestions(doc_type, extracted_text)
        document.suggested_fields = json.dumps(suggestions)
        
        # Update status
        document.status = "completed"
        db.commit()
        
        return {"status": "completed", "document_id": document_id}
        
    except Exception as e:
        document.status = "failed"
        document.error_message = str(e)
        db.commit()
        return {"error": str(e)}
    finally:
        db.close()