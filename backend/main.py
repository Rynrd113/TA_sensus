# backend/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import logging

# Import router
from api.v1.sensus_router import router as sensus_router
from api.v1.prediksi_router import router as prediksi_router
from api.v1.dashboard_router import router as dashboard_router
from api.v1.indikator_router import router as indikator_router
from api.v1.export_router import router as export_router
from api.v1.standards_router import router as standards_router
from api.v1.auth_router import router as auth_router
from api.v1.bangsal_router import router as bangsal_router

# Import untuk database
from database.engine import engine
from models.sensus import Base
from models.user import User, UserSession, UserLoginLog  
from models.bangsal import Bangsal, KamarBangsal
from core.logging_config import log_error
from tasks.scheduler import start_scheduler_thread

# Buat tabel saat startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sensus Harian Rawat Inap", 
    version="1.0",
    description="API untuk manajemen sensus harian rumah sakit dengan prediksi BOR"
)

# Global exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors dengan pesan yang user-friendly"""
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        errors.append(f"{field}: {message}")
    
    error_message = "Validasi gagal: " + "; ".join(errors)
    log_error("VALIDATION_ERROR", error_message)
    
    return JSONResponse(
        status_code=422,
        content={
            "detail": error_message,
            "type": "validation_error"
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle semua error yang tidak tertangani"""
    log_error("UNHANDLED_ERROR", f"Path: {request.url.path}, Error: {str(exc)}")
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Terjadi kesalahan sistem. Silakan coba lagi atau hubungi administrator.",
            "type": "internal_error"
        }
    )

# CORS (untuk frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://localhost:5174", 
        "http://localhost:5175", 
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174", 
        "http://127.0.0.1:5175",
        "http://127.0.0.1:3000"
    ],  # Vite & React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with API v1 prefix
app.include_router(auth_router, prefix="/api/v1")
app.include_router(sensus_router, prefix="/api/v1")
app.include_router(prediksi_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")
app.include_router(indikator_router, prefix="/api/v1")
app.include_router(export_router, prefix="/api/v1")
app.include_router(standards_router, prefix="/api/v1")
app.include_router(bangsal_router, prefix="/api/v1")

# Start scheduler for weekly model retraining
start_scheduler_thread()

@app.get("/")
def root():
    return {"message": "API Sensus Harian Rawat Inap Berjalan!"}
