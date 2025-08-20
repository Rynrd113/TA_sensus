# backend/ml/predict.py
import joblib
import pandas as pd
from typing import List, Dict, Any
import os

def predict_bor(hari: int = 7) -> Dict[str, Any]:
    """
    Prediksi BOR untuk beberapa hari ke depan menggunakan SARIMA
    
    Args:
        hari: Jumlah hari yang ingin diprediksi (default 7 untuk satu minggu)
    
    Returns:
        Dictionary berisi prediksi dan rekomendasi
    """
    model_path = "backend/ml/model.pkl"
    
    # Cek apakah model ada
    if not os.path.exists(model_path):
        return {
            "error": "Model SARIMA belum dilatih. Jalankan python backend/ml/train.py dulu.",
            "prediksi": []
        }
    
    try:
        # Load model SARIMA
        model = joblib.load(model_path)
        
        # Prediksi menggunakan SARIMA
        forecast = model.forecast(steps=hari)
        
        # Untuk SARIMA, juga bisa mendapatkan confidence interval
        try:
            forecast_result = model.get_forecast(steps=hari)
            forecast_values = forecast_result.predicted_mean
            conf_int = forecast_result.conf_int()
            
            # Generate tanggal untuk prediksi
            dates = pd.date_range(
                pd.Timestamp.now().date() + pd.Timedelta(days=1),
                periods=hari
            ).strftime("%Y-%m-%d").tolist()
            
            # Format hasil prediksi dengan confidence interval
            prediksi = []
            for i in range(hari):
                prediksi.append({
                    "tanggal": dates[i], 
                    "bor": round(float(forecast_values.iloc[i]), 1),
                    "bor_min": round(float(conf_int.iloc[i, 0]), 1),
                    "bor_max": round(float(conf_int.iloc[i, 1]), 1)
                })
                
        except Exception:
            # Fallback jika confidence interval gagal
            forecast_values = forecast
            dates = pd.date_range(
                pd.Timestamp.now().date() + pd.Timedelta(days=1),
                periods=hari
            ).strftime("%Y-%m-%d").tolist()
            
            prediksi = [
                {"tanggal": dates[i], "bor": round(float(forecast_values[i]), 1)}
                for i in range(hari)
            ]
        
        # Generate rekomendasi berdasarkan prediksi
        max_bor = max(p["bor"] for p in prediksi)
        avg_bor = sum(p["bor"] for p in prediksi) / len(prediksi)
        
        # Analisis trend mingguan (jika prediksi 7 hari)
        if hari >= 7:
            weekly_trend = "📈 Trend mingguan: "
            first_half = sum(p["bor"] for p in prediksi[:hari//2]) / (hari//2)
            second_half = sum(p["bor"] for p in prediksi[hari//2:]) / (len(prediksi) - hari//2)
            
            if second_half > first_half + 2:
                weekly_trend += "Meningkat"
            elif second_half < first_half - 2:
                weekly_trend += "Menurun"
            else:
                weekly_trend += "Stabil"
        else:
            weekly_trend = ""
        
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
        
        if weekly_trend:
            rekomendasi += f" {weekly_trend}"
        
        return {
            "prediksi": prediksi,
            "rekomendasi": rekomendasi,
            "max_bor": round(max_bor, 1),
            "avg_bor": round(avg_bor, 1),
            "model_type": "SARIMA"
        }
        
    except Exception as e:
        return {
            "error": f"Error saat prediksi SARIMA: {str(e)}", 
            "prediksi": []
        }