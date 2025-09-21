"""
Pydantic schemas for SARIMA prediction API
Sesuai dengan penelitian: "Peramalan Indikator Rumah Sakit Berbasis Sensus Harian Rawat Inap dengan Model SARIMA"
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime, date

# Legacy schemas (keep for compatibility)
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

# New SARIMA schemas
class SARIMATrainingRequest(BaseModel):
    """Request schema untuk training model SARIMA"""
    days_back: Optional[int] = Field(
        90, 
        ge=30, 
        le=365, 
        description="Jumlah hari data untuk training (minimum 30 hari)"
    )
    optimize_parameters: Optional[bool] = Field(
        True, 
        description="Optimasi parameter model otomatis"
    )
    target_column: Optional[str] = Field(
        "bor", 
        description="Kolom target untuk prediksi (bor, alos, etc)"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "days_back": 90,
                "optimize_parameters": True,
                "target_column": "bor"
            }
        }

class ConfidenceInterval(BaseModel):
    """Confidence interval untuk prediksi"""
    lower: List[float] = Field(description="Batas bawah confidence interval")
    upper: List[float] = Field(description="Batas atas confidence interval")

class PredictionValues(BaseModel):
    """Nilai prediksi BOR"""
    values: List[float] = Field(description="Nilai prediksi BOR (%)")
    dates: List[str] = Field(description="Tanggal prediksi (YYYY-MM-DD)")
    confidence_interval: Optional[ConfidenceInterval] = Field(description="Confidence interval")
    average_predicted_bor: float = Field(description="Rata-rata BOR prediksi (%)")

class ClinicalInterpretation(BaseModel):
    """Interpretasi klinis hasil prediksi"""
    high_risk_days: int = Field(description="Jumlah hari dengan risiko BOR tinggi (>85%)")
    low_utilization_days: int = Field(description="Jumlah hari dengan utilisasi rendah (<60%)")
    optimal_days: int = Field(description="Jumlah hari dengan BOR optimal (60-85%)")
    average_predicted_bor: float = Field(description="Rata-rata BOR prediksi")
    warnings: Dict[str, bool] = Field(description="Warning flags")
    recommendations: List[str] = Field(description="Rekomendasi manajemen")

class ModelPerformance(BaseModel):
    """Performa model SARIMA"""
    last_training_mape: float = Field(description="MAPE terakhir (%)")
    meets_journal_criteria: bool = Field(description="Memenuhi kriteria jurnal (MAPE < 10%)")
    model_parameters: Dict[str, Any] = Field(description="Parameter model")

class ClinicalAlerts(BaseModel):
    """Alert klinis berdasarkan prediksi"""
    high_occupancy_warning: bool = Field(description="Warning BOR tinggi")
    low_occupancy_warning: bool = Field(description="Warning BOR rendah")  
    recommendations: List[str] = Field(description="Rekomendasi tindakan")

class SARIMAPredictionResponse(BaseModel):
    """Response schema untuk prediksi SARIMA"""
    status: str = Field(description="Status response")
    forecast_period: int = Field(description="Periode prediksi (hari)")
    predictions: PredictionValues = Field(description="Hasil prediksi")
    interpretation: ClinicalInterpretation = Field(description="Interpretasi klinis")
    model_performance: ModelPerformance = Field(description="Performa model")
    clinical_alerts: ClinicalAlerts = Field(description="Alert klinis")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "forecast_period": 7,
                "predictions": {
                    "values": [78.5, 82.1, 79.8, 77.2, 81.5, 85.2, 83.1],
                    "dates": ["2025-09-22", "2025-09-23", "2025-09-24", "2025-09-25", "2025-09-26", "2025-09-27", "2025-09-28"],
                    "confidence_interval": {
                        "lower": [75.2, 78.8, 76.5, 73.9, 78.2, 81.9, 79.8],
                        "upper": [81.8, 85.4, 83.1, 80.5, 84.8, 88.5, 86.4]
                    },
                    "average_predicted_bor": 81.2
                },
                "interpretation": {
                    "high_risk_days": 1,
                    "low_utilization_days": 0,
                    "optimal_days": 6,
                    "average_predicted_bor": 81.2,
                    "warnings": {
                        "overutilization_risk": True,
                        "underutilization_risk": False
                    },
                    "recommendations": [
                        "Monitor antrian pasien masuk",
                        "Pertahankan tingkat occupancy saat ini"
                    ]
                },
                "model_performance": {
                    "last_training_mape": 7.8,
                    "meets_journal_criteria": True,
                    "model_parameters": {
                        "order": [1, 1, 1],
                        "seasonal_order": [1, 1, 1, 7]
                    }
                },
                "clinical_alerts": {
                    "high_occupancy_warning": True,
                    "low_occupancy_warning": False,
                    "recommendations": [
                        "Monitor antrian pasien masuk"
                    ]
                }
            }
        }