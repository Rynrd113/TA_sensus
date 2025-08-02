# backend/schemas/prediksi.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class PrediksiItem(BaseModel):
    """Schema untuk satu item prediksi"""
    tanggal: str
    bor: float

class PrediksiResponse(BaseModel):
    """Schema untuk response prediksi BOR"""
    prediksi: List[PrediksiItem]
    rekomendasi: Optional[str] = None
    status: Optional[str] = None
    error: Optional[str] = None

class RetrainResponse(BaseModel):
    """Schema untuk response retrain model"""
    message: Optional[str] = None
    status: str
    error: Optional[str] = None