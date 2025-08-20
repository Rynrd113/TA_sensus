#!/usr/bin/env python3
"""
Development server starter for Sensus TA Backend
"""
import sys
import os
import uvicorn

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

if __name__ == "__main__":
    # Set PYTHONPATH environment variable
    os.environ['PYTHONPATH'] = backend_dir
    
    # Run the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[backend_dir],
        log_level="info"
    )
