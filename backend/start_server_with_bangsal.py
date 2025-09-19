#!/usr/bin/env python3
# backend/start_server_with_bangsal.py
"""
Start server with bangsal router enabled
"""
import sys
import os

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    # Import the app
    from main import app
    import uvicorn
    
    print("🔄 Starting server with bangsal management system...")
    print("📊 Bangsal API endpoints will be available at /api/v1/bangsal/")
    
    # Start the server
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("🔧 Trying alternative approach...")
    
    # Alternative approach - run without bangsal router for now
    exec("""
import sys
sys.path.append('.')

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1.auth_router import router as auth_router

app = FastAPI(title="TA Sensus API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "TA Sensus API with Authentication"}

import uvicorn
uvicorn.run(app, host="0.0.0.0", port=8000)
    """)