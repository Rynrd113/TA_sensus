#!/usr/bin/env python3
# backend/start_bangsal_server.py
"""
Startup script for the backend server with bangsal management
"""
import sys
import os

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_dir)

# Now import and run the server
import uvicorn
from main import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)