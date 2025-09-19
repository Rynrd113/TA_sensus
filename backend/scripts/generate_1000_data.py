#!/usr/bin/env python3
"""
Script untuk generate 1000 data sensus realistic dari Januari 2024 - September 2025
Data akan mengikuti pola-pola yang realistis untuk rumah sakit:
- Seasonal patterns (liburan, musim sakit)
- Weekend effects (admission/discharge patterns)
- Random variations yang masuk akal
"""

import sys
import os
from datetime import date, timedelta
from typing import List, Tuple
import random
import math

# Add backend path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from database.session import SessionLocal
from models.sensus import SensusHarian, Base
from database.engine import engine

# Set random seed untuk reproducible results
random.seed(42)

class SensusDataGenerator:
    def __init__(self):
        self.base_capacity = 100  # Base tempat tidur
        self.capacity_variations = [90, 100, 110, 120, 100]  # Variasi kapasitas bulanan
        
        # Seasonal factors (Jan=1, Feb=2, ..., Dec=12)
        self.seasonal_factors = {
            1: 1.2,   # Januari - tinggi (post holiday)
            2: 1.15,  # Februari - tinggi (flu season)
            3: 1.1,   # Maret - normal+
            4: 1.0,   # April - normal
            5: 0.95,  # Mei - rendah
            6: 0.9,   # Juni - rendah (liburan sekolah)
            7: 0.85,  # Juli - terendah (liburan)
            8: 0.9,   # Agustus - rendah
            9: 1.0,   # September - normal
            10: 1.05, # Oktober - normal+
            11: 1.1,  # November - tinggi
            12: 1.25  # Desember - tertinggi (holiday stress)
        }
        
        # Weekend effects
        self.weekend_admission_factor = 0.7  # Weekend admission biasanya lebih rendah
        self.weekend_discharge_factor = 0.8  # Weekend discharge lebih rendah
    
    def get_seasonal_factor(self, date_obj: date) -> float:
        """Get seasonal factor berdasarkan bulan"""
        return self.seasonal_factors.get(date_obj.month, 1.0)
    
    def is_weekend(self, date_obj: date) -> bool:
        """Check apakah weekend (Saturday=5, Sunday=6)"""
        return date_obj.weekday() >= 5
    
    def is_holiday_period(self, date_obj: date) -> bool:
        """Check periode liburan yang berpengaruh ke admission"""
        month, day = date_obj.month, date_obj.day
        
        # Periode liburan nasional
        holidays = [
            (1, 1),   # New Year
            (12, 25), # Christmas
            (8, 17),  # Independence Day
        ]
        
        # Liburan rentang
        if month == 12 and day >= 20:  # Christmas period
            return True
        if month == 1 and day <= 7:   # New Year period
            return True
        if month == 6 and 15 <= day <= 25:  # School holiday mid year
            return True
        if month == 7:  # Peak holiday season
            return True
            
        return (month, day) in holidays
    
    def calculate_capacity(self, date_obj: date) -> int:
        """Calculate tempat tidur tersedia dengan variasi bulanan"""
        base_idx = (date_obj.month - 1) % len(self.capacity_variations)
        base_capacity = self.capacity_variations[base_idx]
        
        # Random variation ±5
        variation = random.randint(-5, 5)
        return max(80, base_capacity + variation)
    
    def calculate_base_occupancy(self, date_obj: date, capacity: int) -> Tuple[int, int, int]:
        """
        Calculate occupancy berdasarkan faktor-faktor realistis
        Returns: (pasien_awal, masuk, keluar)
        """
        seasonal = self.get_seasonal_factor(date_obj)
        is_wknd = self.is_weekend(date_obj)
        is_holiday = self.is_holiday_period(date_obj)
        
        # Base occupancy rate target (70-90%)
        target_occupancy = 0.8 * seasonal
        if is_holiday:
            target_occupancy *= 0.85  # Holiday biasanya lebih rendah
        
        target_occupancy = min(0.95, max(0.6, target_occupancy))
        
        # Calculate pasien awal (dari hari sebelumnya)
        base_pasien_awal = int(capacity * target_occupancy)
        pasien_awal = base_pasien_awal + random.randint(-5, 5)
        pasien_awal = max(0, min(capacity-5, pasien_awal))
        
        # Calculate admission
        base_admission_rate = 0.12  # 12% dari capacity per hari
        admission_factor = seasonal
        
        if is_wknd:
            admission_factor *= self.weekend_admission_factor
        if is_holiday:
            admission_factor *= 0.7
            
        expected_masuk = capacity * base_admission_rate * admission_factor
        masuk = max(0, int(expected_masuk + random.normalvariate(0, expected_masuk * 0.3)))
        masuk = min(masuk, capacity - pasien_awal)  # Tidak bisa melebihi kapasitas
        
        # Calculate discharge (harus realistis dengan LOS)
        # Average LOS sekitar 4-7 hari
        avg_los = random.uniform(4.0, 7.0)
        expected_keluar = (pasien_awal + masuk) / avg_los
        
        discharge_factor = 1.0
        if is_wknd:
            discharge_factor *= self.weekend_discharge_factor
        if is_holiday:
            discharge_factor *= 0.8
            
        keluar = max(0, int(expected_keluar * discharge_factor + random.normalvariate(0, 2)))
        keluar = min(keluar, pasien_awal + masuk)  # Tidak bisa discharge lebih dari yang ada
        
        return pasien_awal, masuk, keluar
    
    def calculate_hari_rawat(self, pasien_awal: int, masuk: int, keluar: int) -> int:
        """Calculate hari rawat yang realistis"""
        if keluar == 0:
            return pasien_awal + masuk
        
        # Estimate berdasarkan rata-rata LOS 4-7 hari
        avg_los = random.uniform(4.0, 7.0)
        total_patient_days = keluar * avg_los
        
        # Add current patients contribution
        total_patient_days += (pasien_awal + masuk - keluar)
        
        return max(0, int(total_patient_days))
    
    def calculate_indicators(self, pasien_awal: int, masuk: int, keluar: int, 
                           capacity: int, hari_rawat: int) -> Tuple[float, float, float, float]:
        """Calculate semua indikator"""
        pasien_akhir = pasien_awal + masuk - keluar
        
        # BOR - Bed Occupancy Rate
        bor = round((pasien_akhir / capacity) * 100, 1) if capacity > 0 else 0.0
        
        # LOS - Length of Stay
        los = round(hari_rawat / keluar, 1) if keluar > 0 else 0.0
        
        # BTO - Bed Turnover
        bto = round(keluar / capacity, 1) if capacity > 0 else 0.0
        
        # TOI - Turn Over Interval
        empty_beds = max(0, capacity - pasien_akhir)
        toi = round(empty_beds / keluar, 1) if keluar > 0 else 0.0
        
        return bor, los, bto, toi
    
    def generate_realistic_data(self, start_date: date, end_date: date) -> List[dict]:
        """Generate data realistis untuk periode tertentu"""
        data_list = []
        current_date = start_date
        
        print(f"🔄 Generating data dari {start_date} sampai {end_date}")
        
        while current_date <= end_date:
            capacity = self.calculate_capacity(current_date)
            pasien_awal, masuk, keluar = self.calculate_base_occupancy(current_date, capacity)
            hari_rawat = self.calculate_hari_rawat(pasien_awal, masuk, keluar)
            
            bor, los, bto, toi = self.calculate_indicators(
                pasien_awal, masuk, keluar, capacity, hari_rawat
            )
            
            data_item = {
                'tanggal': current_date,
                'jml_pasien_awal': pasien_awal,
                'jml_masuk': masuk,
                'jml_keluar': keluar,
                'jml_pasien_akhir': pasien_awal + masuk - keluar,
                'tempat_tidur_tersedia': capacity,
                'hari_rawat': hari_rawat,
                'bor': bor,
                'los': los,
                'bto': bto,
                'toi': toi
            }
            
            data_list.append(data_item)
            current_date += timedelta(days=1)
        
        return data_list

def clear_existing_data(db_session):
    """Clear semua data sensus yang ada"""
    print("🗑️  Menghapus data sensus yang ada...")
    count = db_session.query(SensusHarian).count()
    if count > 0:
        db_session.query(SensusHarian).delete()
        db_session.commit()
        print(f"✅ {count} data lama berhasil dihapus")
    else:
        print("ℹ️  Tidak ada data lama untuk dihapus")

def insert_data_batch(db_session, data_list: List[dict], batch_size: int = 100):
    """Insert data dalam batch untuk performa lebih baik"""
    total = len(data_list)
    print(f"📥 Memasukkan {total} data ke database...")
    
    for i in range(0, total, batch_size):
        batch = data_list[i:i + batch_size]
        
        # Create SensusHarian objects
        sensus_objects = [
            SensusHarian(
                tanggal=item['tanggal'],
                jml_pasien_awal=item['jml_pasien_awal'],
                jml_masuk=item['jml_masuk'],
                jml_keluar=item['jml_keluar'],
                jml_pasien_akhir=item['jml_pasien_akhir'],
                tempat_tidur_tersedia=item['tempat_tidur_tersedia'],
                hari_rawat=item['hari_rawat'],
                bor=item['bor'],
                los=item['los'],
                bto=item['bto'],
                toi=item['toi']
            )
            for item in batch
        ]
        
        db_session.add_all(sensus_objects)
        db_session.commit()
        
        progress = min(i + batch_size, total)
        print(f"📊 Progress: {progress}/{total} ({(progress/total)*100:.1f}%)")

def validate_data(db_session):
    """Validasi data yang sudah dimasukkan"""
    print("\n🔍 Validasi data yang dimasukkan:")
    
    total_count = db_session.query(SensusHarian).count()
    print(f"📊 Total records: {total_count}")
    
    # Date range
    min_date = db_session.query(SensusHarian.tanggal).order_by(SensusHarian.tanggal.asc()).first()[0]
    max_date = db_session.query(SensusHarian.tanggal).order_by(SensusHarian.tanggal.desc()).first()[0]
    print(f"📅 Range tanggal: {min_date} s/d {max_date}")
    
    # BOR statistics
    from sqlalchemy import func
    bor_stats = db_session.query(
        func.avg(SensusHarian.bor).label('avg_bor'),
        func.min(SensusHarian.bor).label('min_bor'),
        func.max(SensusHarian.bor).label('max_bor')
    ).first()
    
    print(f"🏥 BOR - Min: {bor_stats.min_bor:.1f}%, Max: {bor_stats.max_bor:.1f}%, Rata-rata: {bor_stats.avg_bor:.1f}%")
    
    # Capacity statistics
    capacity_stats = db_session.query(
        func.avg(SensusHarian.tempat_tidur_tersedia).label('avg_capacity'),
        func.min(SensusHarian.tempat_tidur_tersedia).label('min_capacity'),
        func.max(SensusHarian.tempat_tidur_tersedia).label('max_capacity')
    ).first()
    
    print(f"🛏️  Kapasitas - Min: {capacity_stats.min_capacity}, Max: {capacity_stats.max_capacity}, Rata-rata: {capacity_stats.avg_capacity:.0f}")

def main():
    """Main function untuk generate 1000 data"""
    print("🚀 Generator Data Sensus 1000 Records (2024-2025)")
    print("=" * 60)
    
    # Create tables if not exists
    Base.metadata.create_all(bind=engine)
    
    # Date range: Generate exactly 1000+ data points
    start_date = date(2024, 1, 1)
    target_records = 1000
    
    # Calculate end date to get 1000+ records
    end_date = start_date + timedelta(days=target_records - 1)
    total_days = (end_date - start_date).days + 1
    
    print(f"📅 Target: {target_records} records")
    print(f"📅 Periode: {start_date} s/d {end_date} ({total_days} hari)")
    
    # Initialize generator
    generator = SensusDataGenerator()
    
    # Database session
    db = SessionLocal()
    try:
        # Clear existing data
        clear_existing_data(db)
        
        # Generate realistic data
        print(f"\n🎲 Generating {total_days} data dengan pola realistis...")
        data_list = generator.generate_realistic_data(start_date, end_date)
        
        # Insert to database
        print(f"\n💾 Menyimpan data ke database...")
        insert_data_batch(db, data_list)
        
        # Validate results
        validate_data(db)
        
        print("\n" + "=" * 60)
        print("✅ SUCCESS! Data sensus berhasil di-generate!")
        print(f"📊 Total: {len(data_list)} records")
        print("🌐 Akses frontend: http://localhost:5174")
        print("📚 API docs: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()