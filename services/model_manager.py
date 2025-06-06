
# services/model_manager.py
class ModelManager:
    def __init__(self):
        self.models = {}
        self.load_available_models()
    
    def load_available_models(self):
        """Load information about available models"""
        try:
            result = subprocess.run([
                "ollama", "list"
            ], capture_output=True, text=True)
            
            # Parse ollama list output
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            
            for line in lines:
                parts = line.split()
                if len(parts