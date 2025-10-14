# backend/api/v1/prediksi_router.py
from fastapi import APIRouter, HTTPException, Request, Body
import joblib
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
import os
import json
from datetime import datetime
from pydantic import BaseModel, Field

from schemas.prediksi import PrediksiResponse, RetrainResponse
from core.logging_config import log_prediction, log_error

router = APIRouter(prefix="/prediksi", tags=["prediksi"])

# Global model cache untuk menghindari load berulang
_MODEL_CACHE = {
    "model": None,
    "model_info": None,
    "loaded_at": None
}

# NEW: Request schema untuk endpoint POST /api/v1/prediksi
class PrediksiRequest(BaseModel):
    n_days: int = Field(default=7, ge=1, le=30, description="Jumlah hari prediksi (1-30)")
    confidence_interval: float = Field(default=0.95, ge=0.80, le=0.99, description="Confidence interval (0.80-0.99)")
    
    class Config:
        schema_extra = {
            "example": {
                "n_days": 7,
                "confidence_interval": 0.95
            }
        }

# NEW: Response schema sesuai requirement
class PredictionItem(BaseModel):
    date: str = Field(description="Tanggal prediksi (YYYY-MM-DD)")
    predicted_value: float = Field(description="Nilai prediksi BOR (%)")
    lower_bound: float = Field(description="Batas bawah confidence interval")
    upper_bound: float = Field(description="Batas atas confidence interval")

class ModelInfo(BaseModel):
    model_type: str = Field(description="Tipe model SARIMA")
    mape: float = Field(description="Mean Absolute Percentage Error (%)")
    last_trained: str = Field(description="Tanggal terakhir training")
    rmse: Optional[float] = Field(None, description="Root Mean Squared Error")
    mae: Optional[float] = Field(None, description="Mean Absolute Error")

class PrediksiResponseNew(BaseModel):
    predictions: List[PredictionItem] = Field(description="Daftar prediksi BOR")
    model_info: ModelInfo = Field(description="Informasi model")
    status: str = Field(default="success")
    error: Optional[str] = Field(None)

def load_model_with_cache():
    """Load SARIMA model dengan caching untuk performa optimal"""
    global _MODEL_CACHE
    
    # Cek apakah model sudah di-cache
    if _MODEL_CACHE["model"] is not None:
        return _MODEL_CACHE["model"], _MODEL_CACHE["model_info"]
    
    # Load model dari file (support relative dan absolute path)
    possible_paths = [
        "backend/models/sarima_model.pkl",
        "models/sarima_model.pkl",
        os.path.join(os.path.dirname(__file__), "../../models/sarima_model.pkl")
    ]
    
    model_path = None
    for path in possible_paths:
        if os.path.exists(path):
            model_path = path
            break
    
    if model_path is None:
        raise FileNotFoundError("Model SARIMA belum dilatih. Jalankan training terlebih dahulu.")
    
    # Training log path
    training_log_path = model_path.replace("sarima_model.pkl", "training_log.json")
    
    # Load model
    model = joblib.load(model_path)
    
    # Load model info dari training log
    model_info = None
    if os.path.exists(training_log_path):
        with open(training_log_path, 'r') as f:
            training_log = json.load(f)
            model_info = {
                "model_type": training_log.get("model_info", {}).get("model_formula", "SARIMA"),
                "mape": round(training_log.get("model_performance", {}).get("mape", 0), 2),
                "rmse": round(training_log.get("model_performance", {}).get("rmse", 0), 2),
                "mae": round(training_log.get("model_performance", {}).get("mae", 0), 2),
                "last_trained": training_log.get("training_timestamp", "unknown"),
                "aic": round(training_log.get("model_statistics", {}).get("aic", 0), 2),
                "bic": round(training_log.get("model_statistics", {}).get("bic", 0), 2)
            }
    else:
        # Default model info jika training log tidak ada
        model_info = {
            "model_type": "SARIMA(1,1,1)(1,0,1)7",
            "mape": 0.0,
            "rmse": 0.0,
            "mae": 0.0,
            "last_trained": datetime.now().isoformat(),
            "aic": 0.0,
            "bic": 0.0
        }
    
    # Cache model dan info
    _MODEL_CACHE["model"] = model
    _MODEL_CACHE["model_info"] = model_info
    _MODEL_CACHE["loaded_at"] = datetime.now()
    
    return model, model_info

# NEW: POST endpoint sesuai requirement dengan confidence interval
@router.post("", response_model=PrediksiResponseNew, name="Prediksi BOR (SARIMA)", 
            description="Endpoint utama untuk prediksi BOR dengan model SARIMA")
async def predict_with_confidence_interval(request: PrediksiRequest = Body(...)):
    """
    Prediksi BOR untuk n_days ke depan dengan confidence interval
    
    - **n_days**: Jumlah hari prediksi (1-30)
    - **confidence_interval**: Tingkat kepercayaan (0.80-0.99)
    
    Returns predictions dengan upper/lower bounds untuk setiap hari
    """
    try:
        # Load model dengan caching
        model, model_info = load_model_with_cache()
        
        # Prediksi dengan confidence interval
        forecast_result = model.get_forecast(steps=request.n_days)
        predicted_mean = forecast_result.predicted_mean
        
        # Get confidence interval
        conf_int = forecast_result.conf_int(alpha=1-request.confidence_interval)
        
        # Generate dates
        dates = pd.date_range(
            start=pd.Timestamp.now().date() + pd.Timedelta(days=1),
            periods=request.n_days,
            freq='D'
        )
        
        # Build response
        predictions = []
        for i in range(request.n_days):
            prediction_item = PredictionItem(
                date=dates[i].strftime("%Y-%m-%d"),
                predicted_value=round(float(predicted_mean.iloc[i]), 1),
                lower_bound=round(float(conf_int.iloc[i, 0]), 1),
                upper_bound=round(float(conf_int.iloc[i, 1]), 1)
            )
            predictions.append(prediction_item)
        
        # Format last_trained date
        last_trained_str = model_info["last_trained"]
        if 'T' in last_trained_str:
            last_trained_dt = datetime.fromisoformat(last_trained_str.replace('Z', '+00:00'))
            last_trained_formatted = last_trained_dt.strftime("%Y-%m-%d")
        else:
            last_trained_formatted = last_trained_str
        
        # Build model info
        model_info_obj = ModelInfo(
            model_type=model_info["model_type"],
            mape=model_info["mape"],
            rmse=model_info.get("rmse"),
            mae=model_info.get("mae"),
            last_trained=last_trained_formatted
        )
        
        # Log prediction
        log_prediction(request.n_days, [p.dict() for p in predictions])
        
        return PrediksiResponseNew(
            predictions=predictions,
            model_info=model_info_obj,
            status="success"
        )
        
    except FileNotFoundError as e:
        log_error("PREDICT_SARIMA", f"Model not found: {str(e)}")
        raise HTTPException(
            status_code=404,
            detail="Model SARIMA belum dilatih. Jalankan training melalui endpoint /retrain"
        )
    except Exception as e:
        log_error("PREDICT_SARIMA", f"Prediction error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error saat prediksi: {str(e)}"
        )


# LEGACY: Endpoint lama (backward compatibility)
@router.get("/bor", response_model=PrediksiResponse)
def predict_bor_next_days(hari: int = 3):
    """[LEGACY] Prediksi BOR untuk beberapa hari ke depan - gunakan POST /prediksi untuk fitur lengkap"""
    model_path = "backend/models/sarima_model.pkl"
    
    # Validasi input
    if hari < 1 or hari > 30:
        return PrediksiResponse(
            error="Jumlah hari prediksi harus antara 1-30",
            prediksi=[],
            status="error"
        )
    
    try:
        # Load model dengan cache
        model, model_info = load_model_with_cache()
        
        # Prediksi menggunakan SARIMA
        forecast = model.forecast(steps=hari)
        dates = pd.date_range(
            pd.Timestamp.now().date() + pd.Timedelta(days=1),
            periods=hari
        ).strftime("%Y-%m-%d").tolist()

        prediksi = [
            {"tanggal": dates[i], "bor": max(0.0, min(100.0, round(float(forecast[i]), 1)))}
            for i in range(hari)
        ]

        # Rekomendasi berdasarkan prediksi BOR
        max_bor = max(p["bor"] for p in prediksi)
        avg_bor = sum(p["bor"] for p in prediksi) / len(prediksi)
        
        if max_bor > 95:
            rekomendasi = "⚠️ KRITIS: BOR diprediksi >95%. Aktifkan protokol darurat!"
        elif max_bor > 85:
            rekomendasi = "⚠️ TINGGI: BOR diprediksi >85%. Siapkan rencana kontinjensi."
        elif avg_bor > 75:
            rekomendasi = "📊 NORMAL-TINGGI: BOR rata-rata >75%. Pantau terus."
        else:
            rekomendasi = "✅ NORMAL: BOR diprediksi dalam batas aman."

        # Log aktivitas prediksi
        log_prediction(hari, prediksi)

        return PrediksiResponse(
            prediksi=prediksi,
            rekomendasi=rekomendasi,
            status="success"
        )
        
    except FileNotFoundError:
        log_error("PREDICT_BOR", "Model file not found")
        return PrediksiResponse(
            error="Model belum dilatih. Jalankan training dulu melalui endpoint /retrain",
            prediksi=[],
            status="error"
        )
    except Exception as e:
        log_error("PREDICT_BOR", f"Error during prediction: {str(e)}")
        return PrediksiResponse(
            error=f"Error saat prediksi: {str(e)}", 
            prediksi=[],
            status="error"
        )

@router.post("/retrain", response_model=RetrainResponse, name="Retrain SARIMA Model")
def retrain_model():
    """Endpoint untuk melatih ulang model SARIMA dengan logging"""
    try:
        # Clear model cache
        global _MODEL_CACHE
        _MODEL_CACHE = {
            "model": None,
            "model_info": None,
            "loaded_at": None
        }
        
        # Import training function
        from ml.train import train_sarima_and_save
        
        log_prediction(0, [{"action": "MODEL_RETRAIN", "status": "starting"}])
        success = train_sarima_and_save()
        
        if success:
            log_prediction(0, [{"action": "MODEL_RETRAIN", "status": "success"}])
            return RetrainResponse(
                message="Model SARIMA berhasil dilatih ulang dan siap digunakan", 
                status="success"
            )
        else:
            log_error("MODEL_RETRAIN", "Failed to retrain - insufficient data")
            return RetrainResponse(
                error="Gagal melatih model. Pastikan data sensus cukup (minimal 30 hari)", 
                status="error"
            )
            
    except ImportError as e:
        log_error("MODEL_RETRAIN", f"Import error: {str(e)}")
        return RetrainResponse(
            error="Modul training tidak ditemukan. Periksa dependencies", 
            status="error"
        )
    except Exception as e:
        log_error("MODEL_RETRAIN", f"Unexpected error: {str(e)}")
        return RetrainResponse(
            error=f"Error tidak terduga: {str(e)}", 
            status="error"
        )


# NEW: Endpoint untuk cek status model
@router.get("/status", name="Model Status")
def get_model_status():
    """Get status dan informasi model SARIMA yang sedang aktif"""
    try:
        model, model_info = load_model_with_cache()
        
        return {
            "status": "ready",
            "model_loaded": True,
            "model_info": model_info,
            "cached_at": _MODEL_CACHE["loaded_at"].isoformat() if _MODEL_CACHE["loaded_at"] else None,
            "message": "Model SARIMA siap untuk prediksi"
        }
    except FileNotFoundError:
        return {
            "status": "not_trained",
            "model_loaded": False,
            "model_info": None,
            "cached_at": None,
            "message": "Model SARIMA belum dilatih. Jalankan endpoint /retrain"
        }
    except Exception as e:
        return {
            "status": "error",
            "model_loaded": False,
            "model_info": None,
            "cached_at": None,
            "message": f"Error: {str(e)}"
        }