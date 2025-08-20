# backend/database/init_db.py
"""
Script untuk inisialisasi database dan buat contoh data
"""
from datetime import date, timedelta
from models.sensus import Base, SensusHarian
from database.engine import engine
from database.session import SessionLocal
import random

def create_tables():
    """Buat semua tabel di database"""
    print("🔄 Membuat tabel database...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tabel berhasil dibuat!")

def create_sample_data():
    """Buat data contoh untuk testing"""
    db = SessionLocal()
    try:
        # Cek apakah sudah ada data
        existing = db.query(SensusHarian).first()
        if existing:
            print("📊 Data sudah ada di database")
            return
        
        print("🔄 Membuat data contoh...")
        
        # Buat data 30 hari terakhir
        start_date = date.today() - timedelta(days=30)
        
        for i in range(30):
            current_date = start_date + timedelta(days=i)
            
            # Simulasi data realistis
            tempat_tidur = 50
            pasien_awal = random.randint(35, 45)
            masuk = random.randint(5, 15)
            keluar = random.randint(3, 12)
            hari_rawat = random.randint(keluar * 2, keluar * 5) if keluar > 0 else 0
            
            pasien_akhir = pasien_awal + masuk - keluar
            bor = round((pasien_akhir / tempat_tidur) * 100, 1)
            los = round(hari_rawat / keluar, 1) if keluar > 0 else 0.0
            bto = round(keluar / tempat_tidur, 1)
            toi = round(max(0, tempat_tidur - pasien_akhir) / keluar, 1) if keluar > 0 else 0.0
            
            sensus = SensusHarian(
                tanggal=current_date,
                jml_pasien_awal=pasien_awal,
                jml_masuk=masuk,
                jml_keluar=keluar,
                jml_pasien_akhir=pasien_akhir,
                tempat_tidur_tersedia=tempat_tidur,
                hari_rawat=hari_rawat,  # Simpan hari_rawat untuk LOS
                bor=bor,
                los=los,
                bto=bto,
                toi=toi
            )
            db.add(sensus)
        
        db.commit()
        print("✅ Data contoh berhasil dibuat! (30 hari)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

def init_database():
    """Inisialisasi database lengkap"""
    print("🚀 Inisialisasi Database Sensus RS")
    print("=" * 40)
    
    create_tables()
    create_sample_data()
    
    print("=" * 40)
    print("✅ Database siap digunakan!")
    print("📊 Akses Swagger UI: http://localhost:8000/docs")
    print("🌐 Frontend: http://localhost:5173")

if __name__ == "__main__":
    init_database()