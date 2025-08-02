# backend/api/v1/prediksi_router.py
from fastapi import APIRouter, HTTPException
import joblib
import pandas as pd
from typing import List
import os
from backend.schemas.prediksi import PrediksiResponse, RetrainResponse
from backend.core.logging_config import log_prediction, log_error

router = APIRouter(prefix="/prediksi", tags=["prediksi"])

@router.get("/bor", response_model=PrediksiResponse)
def predict_bor_next_days(hari: int = 3):
    """Prediksi BOR untuk beberapa hari ke depan menggunakan model ARIMA"""
    model_path = "backend/ml/model.pkl"
    
    # Validasi input
    if hari < 1 or hari > 30:
        return PrediksiResponse(
            error="Jumlah hari prediksi harus antara 1-30",
            prediksi=[],
            status="error"
        )
    
    try:
        # Periksa apakah file model ada
        if not os.path.exists(model_path):
            log_error("PREDICT_BOR", "Model file not found")
            return PrediksiResponse(
                error="Model belum dilatih. Jalankan training dulu melalui endpoint /retrain",
                prediksi=[],
                status="error"
            )
            
        model = joblib.load(model_path)
        
        # Prediksi
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
        
    except Exception as e:
        log_error("PREDICT_BOR", f"Error during prediction: {str(e)}")
        return PrediksiResponse(
            error=f"Error saat prediksi: {str(e)}", 
            prediksi=[],
            status="error"
        )

@router.post("/retrain", response_model=RetrainResponse)
def retrain_model():
    """Endpoint untuk melatih ulang model ARIMA dengan logging"""
    try:
        from backend.ml.train import train_arima_and_save
        
        log_error("MODEL_RETRAIN", "Starting model retraining...")
        success = train_arima_and_save()
        
        if success:
            log_error("MODEL_RETRAIN", "Model retrained successfully")
            return RetrainResponse(
                message="Model berhasil dilatih ulang dan siap digunakan", 
                status="success"
            )
        else:
            log_error("MODEL_RETRAIN", "Failed to retrain - insufficient data")
            return RetrainResponse(
                error="Gagal melatih model. Pastikan data sensus cukup (minimal 10 hari)", 
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