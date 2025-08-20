# backend/ml/train.py
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
import joblib
import os
from sqlalchemy.orm import Session

from database.session import SessionLocal
from models.sensus import SensusHarian

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

def train_sarima_and_save():
    """Latih model SARIMA dan simpan dengan robust error handling"""
    try:
        # Pastikan direktori ml ada
        os.makedirs("backend/ml", exist_ok=True)
        
        df = load_data_from_db()
        if df is None or len(df) < 30:  # SARIMA needs more data for seasonal patterns
            print("❌ Data tidak cukup untuk pelatihan SARIMA (minimal 30 hari)")
            return False

        print(f"📊 Data tersedia: {len(df)} hari, BOR range: {df['bor'].min():.1f}% - {df['bor'].max():.1f}%")

        # Konfigurasi SARIMA dengan komponen seasonal
        # Format: (p,d,q) x (P,D,Q,s) dimana s = seasonal period (7 untuk mingguan)
        sarima_configs = [
            ((1, 1, 1), (1, 1, 1, 7)),  # Basic SARIMA dengan seasonal mingguan
            ((2, 1, 1), (1, 1, 1, 7)),  # Lebih kompleks non-seasonal
            ((1, 1, 2), (1, 1, 1, 7)),  # Variasi MA
            ((1, 1, 1), (0, 1, 1, 7)),  # Seasonal MA only
            ((0, 1, 1), (1, 1, 0, 7)),  # Simple MA + Seasonal AR
        ]
        
        best_model = None
        best_aic = float('inf')
        
        for order, seasonal_order in sarima_configs:
            try:
                model = SARIMAX(df['bor'], 
                              order=order, 
                              seasonal_order=seasonal_order,
                              enforce_stationarity=False,
                              enforce_invertibility=False)
                fitted_model = model.fit(disp=False, maxiter=100)
                
                if fitted_model.aic < best_aic:
                    best_aic = fitted_model.aic
                    best_model = fitted_model
                    print(f"✅ SARIMA{order}x{seasonal_order} berhasil, AIC: {fitted_model.aic:.2f}")
                    
            except Exception as e:
                print(f"⚠️ SARIMA{order}x{seasonal_order} gagal: {str(e)}")
                continue

        if best_model is None:
            print("❌ Semua konfigurasi SARIMA gagal")
            return False

        # Simpan model terbaik
        model_path = "backend/ml/model.pkl"
        joblib.dump(best_model, model_path)
        print(f"✅ Model SARIMA terbaik disimpan di {model_path} (AIC: {best_aic:.2f})")
        
        # Test prediksi sederhana
        try:
            test_forecast = best_model.forecast(steps=7)  # Test prediksi 1 minggu
            print(f"🔮 Test prediksi 7 hari: {[round(f, 1) for f in test_forecast]}")
        except Exception as e:
            print(f"⚠️ Warning: Model tersimpan tapi test prediksi gagal: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error training model: {str(e)}")
        return False

# Jika dijalankan langsung
if __name__ == "__main__":
    print("🚀 Memulai training model SARIMA...")
    success = train_sarima_and_save()
    if success:
        print("🎉 Training SARIMA selesai!")
    else:
        print("💥 Training SARIMA gagal!")
        exit(1)