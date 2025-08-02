# backend/ml/predict.py
import joblib
import pandas as pd
from typing import List, Dict, Any
import os

def predict_bor(hari: int = 3) -> Dict[str, Any]:
    """
    Prediksi BOR untuk beberapa hari ke depan
    
    Args:
        hari: Jumlah hari yang ingin diprediksi (default 3)
    
    Returns:
        Dictionary berisi prediksi dan rekomendasi
    """
    model_path = "backend/ml/model.pkl"
    
    # Cek apakah model ada
    if not os.path.exists(model_path):
        return {
            "error": "Model belum dilatih. Jalankan python backend/ml/train.py dulu.",
            "prediksi": []
        }
    
    try:
        # Load model
        model = joblib.load(model_path)
        
        # Prediksi
        forecast = model.forecast(steps=hari)
        
        # Generate tanggal untuk prediksi
        dates = pd.date_range(
            pd.Timestamp.now().date() + pd.Timedelta(days=1),
            periods=hari
        ).strftime("%Y-%m-%d").tolist()
        
        # Format hasil prediksi
        prediksi = [
            {"tanggal": dates[i], "bor": round(float(forecast[i]), 1)}
            for i in range(hari)
        ]
        
        # Generate rekomendasi berdasarkan prediksi
        max_bor = max(p["bor"] for p in prediksi)
        avg_bor = sum(p["bor"] for p in prediksi) / len(prediksi)
        
        if max_bor > 95:
            rekomendasi = "⚠️ BOR diprediksi >95%. URGENT: Siapkan rencana evakuasi pasien atau buka unit cadangan."
        elif max_bor > 90:
            rekomendasi = "🚨 BOR diprediksi >90%. Pertimbangkan tambah tenaga atau buka kamar cadangan."
        elif avg_bor > 85:
            rekomendasi = "⚡ BOR rata-rata >85%. Pantau kesiapan tempat tidur dan optimasi discharge planning."
        elif avg_bor > 80:
            rekomendasi = "📊 BOR mendekati batas optimal. Pantau trend penerimaan pasien."
        else:
            rekomendasi = "✅ BOR diprediksi dalam batas normal (<80%)."
        
        return {
            "prediksi": prediksi,
            "rekomendasi": rekomendasi,
            "max_bor": round(max_bor, 1),
            "avg_bor": round(avg_bor, 1)
        }
        
    except Exception as e:
        return {
            "error": f"Error saat prediksi: {str(e)}", 
            "prediksi": []
        }