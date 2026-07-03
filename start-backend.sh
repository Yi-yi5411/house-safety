#!/bin/bash
# Start the FastAPI backend server
# Prerequisites: PostgreSQL, Redis, and Ollama should be running

echo "Starting House Safety Assessment Backend..."
cd "$(dirname "$0")/fastapi-backend"
pip install -r requirements.txt 2>/dev/null || echo "Dependencies already installed"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
