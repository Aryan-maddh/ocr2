import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd
from sklearn.model_selection import train_test_split
import subprocess
import tempfile
from pathlib import Path

class LLMTrainingService:
    def __init__(self, base_model: str = "llama3.2:3b"):
        self.base_model = base_model
        self.training_data_dir = "training_data"
        self.models_dir = "custom_models"
        os.makedirs(self.training_data_dir, exist_ok=True)
        os.makedirs(self.models_dir, exist_ok=True)
    
    def prepare_training_data(self, document_type: str, feedback_data: List[Dict]) -> str:
        """Prepare training data from user feedback and corrections"""
        
        training_examples = []
        
        for feedback in feedback_data:
            # Create training example from user corrections
            if feedback.get("corrections") and feedback.get("original_extraction"):
                prompt = self._create_training_prompt(
                    document_type, 
                    feedback["document_text"],
                    feedback["original_extraction"],
                    feedback["corrections"]
                )
                training_examples.append(prompt)
        
        # Save training data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        training_file = os.path.join(
            self.training_data_dir, 
            f"{document_type}_training_{timestamp}.jsonl"
        )
        
        with open(training_file, 'w') as f:
            for example in training_examples:
                f.write(json.dumps(example) + '\n')
        
        return training_file
    
    def _create_training_prompt(self, doc_type: str, text: str, original: Dict, corrected: Dict) -> Dict:
        """Create a training prompt from correction data"""
        
        system_prompt = f"""You are an expert document processor specialized in {doc_type} documents.
        Extract the requested fields accurately from the given text."""
        
        user_prompt = f"""Extract the following fields from this {doc_type}:

        Document text:
        {text}

        Required fields: {', '.join(corrected.keys())}

        Return as JSON with field names as keys and extracted values as values."""
        
        # The corrected version is what the model should learn to output
        assistant_response = json.dumps(corrected)
        
        return {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
                {"role": "assistant", "content": assistant_response}
            ]
        }
    
    def fine_tune_model(self, document_type: str, training_file: str) -> str:
        """Fine-tune a model for specific document type using Ollama"""
        
        model_name = f"ocr_specialist_{document_type}_{datetime.now().strftime('%Y%m%d')}"
        
        # Create Modelfile for fine-tuning
        modelfile_content = f"""FROM {self.base_model}

        # Set parameters for document processing
        PARAMETER temperature 0.1
        PARAMETER top_p 0.9
        PARAMETER repeat_penalty 1.1

        # System message for document processing
        SYSTEM You are an expert document processor specialized in {document_type} documents. 
        You extract information accurately and return structured JSON responses.
        Always include confidence scores for extracted fields.
        """
        
        modelfile_path = os.path.join(self.models_dir, f"{model_name}.Modelfile")
        with open(modelfile_path, 'w') as f:
            f.write(modelfile_content)
        
        try:
            # Create the custom model
            result = subprocess.run([
                "ollama", "create", model_name, "-f", modelfile_path
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"Successfully created model: {model_name}")
                return model_name
            else:
                raise Exception(f"Model creation failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            raise Exception("Model creation timed out")
    
    def evaluate_model_performance(self, model_name: str, test_data: List[Dict]) -> Dict[str, float]:
        """Evaluate model performance on test data"""
        
        total_tests = len(test_data)
        correct_extractions = 0
        field_accuracies = {}
        
        for test_case in test_data:
            document_text = test_case["document_text"]
            expected_fields = test_case["expected_fields"]
            
            # Get model prediction
            prompt = f"""Extract fields from this document and return as JSON:

            {document_text}

            Required fields: {', '.join(expected_fields.keys())}"""
            
            try:
                result = subprocess.run([
                    "ollama", "run", model_name, prompt
                ], capture_output=True, text=True, timeout=60)
                
                # Parse model response
                response_text = result.stdout.strip()
                extracted_data = self._parse_json_response(response_text)
                
                # Calculate accuracy
                field_matches = 0
                total_fields = len(expected_fields)
                
                for field_name, expected_value in expected_fields.items():
                    extracted_value = extracted_data.get(field_name, "")
                    
                    # Normalize and compare
                    if self._normalize_text(str(expected_value)) == self._normalize_text(str(extracted_value)):
                        field_matches += 1
                        
                        # Track per-field accuracy
                        if field_name not in field_accuracies:
                            field_accuracies[field_name] = {"correct": 0, "total": 0}
                        field_accuracies[field_name]["correct"] += 1
                    
                    if field_name not in field_accuracies:
                        field_accuracies[field_name] = {"correct": 0, "total": 0}
                    field_accuracies[field_name]["total"] += 1
                
                if field_matches == total_fields:
                    correct_extractions += 1
                    
            except Exception as e:
                print(f"Error evaluating test case: {e}")
                continue
        
        # Calculate final metrics
        overall_accuracy = correct_extractions / total_tests if total_tests > 0 else 0
        
        field_accuracy_percentages = {}
        for field_name, stats in field_accuracies.items():
            field_accuracy_percentages[field_name] = stats["correct"] / stats["total"] if stats["total"] > 0 else 0
        
        return {
            "overall_accuracy": overall_accuracy,
            "field_accuracies": field_accuracy_percentages,
            "total_tests": total_tests,
            "correct_extractions": correct_extractions
        }
    
    def _parse_json_response(self, response: str) -> Dict:
        """Parse JSON from LLM response"""
        try:
            # Try to find JSON in the response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end != 0:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            
            return {}
        except json.JSONDecodeError:
            return {}
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison"""
        return text.strip().lower().replace(" ", "").replace("-", "").replace(".", "")
    
    def create_training_dataset_from_logs(self, document_type: str, days_back: int = 30) -> str:
        """Create training dataset from processing logs and user corrections"""
        
        # This would query your database for:
        # 1. Documents processed in the last N days
        # 2. Any user corrections or feedback
        # 3. High-confidence extractions as positive examples
        
        # Example implementation (you'd adapt this to your database structure)
        from sqlalchemy.orm import Session
        from models.document import Document, ExtractedData, UserFeedback
        from database import SessionLocal
        
        db = SessionLocal()
        
        try:
            # Get documents with corrections
            documents_with_feedback = db.query(Document).join(UserFeedback).filter(
                Document.document_type == document_type,
                Document.processed_at >= datetime.now() - timedelta(days=days_back)
            ).all()
            
            training_data = []
            
            for doc in documents_with_feedback:
                # Get original extraction
                original_data = {data.field_name: data.field_value 
                               for data in doc.extracted_data}
                
                # Get user corrections
                feedback = doc.feedback[0] if doc.feedback else None
                if feedback and feedback.corrections:
                    training_data.append({
                        "document_text": doc.extracted_text or "",
                        "original_extraction": original_data,
                        "corrections": json.loads(feedback.corrections)
                    })
            
            # Prepare training file
            if training_data:
                return self.prepare_training_data(document_type, training_data)
            else:
                raise Exception("No training data available")
                
        finally:
            db.close()