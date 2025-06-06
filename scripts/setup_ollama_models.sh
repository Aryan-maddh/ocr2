---
# scripts/setup_ollama_models.sh
#!/bin/bash

# Setup script to pull required Ollama models
echo "Setting up Ollama models..."

# Wait for Ollama to be ready
sleep 10

# Pull the main model
ollama pull llama3.2:3b

# Pull additional models for specialized tasks
ollama pull llama3.2:1b  # Faster model for simple tasks
ollama pull codellama:7b  # For code-related document processing

echo "Ollama models setup complete!"
