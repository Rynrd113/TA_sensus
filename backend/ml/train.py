# backend/ml/train.py
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import joblib
import os
from sqlalchemy.orm import Session

from backend.database.session import SessionLocal
from backend.models.sensus import SensusHarian

def load_data_from_db(db: Session = None):
    """Ambil data BOR dari database dengan error handling"""
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    try:
        data = db.query(SensusHarian.tanggal, SensusHarian.bor)\
                 .order_by(SensusHarian.tanggal.asc())\
                 .all()
        
        if not data:
            print("❌ Tidak ada data sensus dalam database")
            return None

        df = pd.DataFrame(data, columns=["tanggal", "bor"])
        df["tanggal"] = pd.to_datetime(df["tanggal"])
        df.set_index("tanggal", inplace=True)

        # Filter nilai BOR yang valid (0-100)
        df = df[(df['bor'] >= 0) & (df['bor'] <= 100)]
        
        if len(df) == 0:
            print("❌ Tidak ada data BOR yang valid")
            return None

        # Resample harian, isi missing dengan interpolasi
        df = df.resample('D').first().interpolate()

        return df
        
    except Exception as e:
        print(f"❌ Error saat load data: {str(e)}")
        return None
    finally:
        if close_db:
            db.close()

def train_arima_and_save():
    """Latih model ARIMA dan simpan dengan robust error handling"""
    try:
        # Pastikan direktori ml ada
        os.makedirs("backend/ml", exist_ok=True)
        
        df = load_data_from_db()
        if df is None or len(df) < 10:
            print("❌ Data tidak cukup untuk pelatihan (minimal 10 hari)")
            return False

        print(f"📊 Data tersedia: {len(df)} hari, BOR range: {df['bor'].min():.1f}% - {df['bor'].max():.1f}%")

        # Coba beberapa konfigurasi ARIMA
        arima_configs = [
            (1, 1, 1),  # Simple ARIMA
            (2, 1, 1),  # Sedikit lebih kompleks
            (1, 1, 2),  # Variasi lain
            (0, 1, 1),  # MA model
        ]
        
        best_model = None
        best_aic = float('inf')
        
        for order in arima_configs:
            try:
                model = ARIMA(df['bor'], order=order)
                fitted_model = model.fit()
                
                if fitted_model.aic < best_aic:
                    best_aic = fitted_model.aic
                    best_model = fitted_model
                    print(f"✅ ARIMA{order} berhasil, AIC: {fitted_model.aic:.2f}")
                    
            except Exception as e:
                print(f"⚠️ ARIMA{order} gagal: {str(e)}")
                continue

        if best_model is None:
            print("❌ Semua konfigurasi ARIMA gagal")
            return False

        # Simpan model terbaik
        model_path = "backend/ml/model.pkl"
        joblib.dump(best_model, model_path)
        print(f"✅ Model terbaik disimpan di {model_path} (AIC: {best_aic:.2f})")
        
        # Test prediksi sederhana
        try:
            test_forecast = best_model.forecast(steps=3)
            print(f"🔮 Test prediksi 3 hari: {[round(f, 1) for f in test_forecast]}")
        except Exception as e:
            print(f"⚠️ Warning: Model tersimpan tapi test prediksi gagal: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error training model: {str(e)}")
        return False

# Jika dijalankan langsung
if __name__ == "__main__":
    print("🚀 Memulai training model ARIMA...")
    success = train_arima_and_save()
    if success:
        print("🎉 Training selesai!")
    else:
        print("💥 Training gagal!")
        exit(1)