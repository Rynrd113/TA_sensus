#!/usr/bin/env python3
"""
Script untuk melihat summary data sensus yang sudah di-generate
"""

import sys
import os

# Add backend path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from database.session import SessionLocal
from models.sensus import SensusHarian
from sqlalchemy import func, extract
from datetime import date

def get_data_summary():
    """Tampilkan summary data sensus yang sudah dimasukkan"""
    db = SessionLocal()
    
    try:
        print("📊 SUMMARY DATA SENSUS YANG SUDAH DI-GENERATE")
        print("=" * 60)
        
        # Basic counts
        total_records = db.query(SensusHarian).count()
        print(f"📈 Total Records: {total_records:,} data")
        
        # Date range
        date_range = db.query(
            func.min(SensusHarian.tanggal).label('start_date'),
            func.max(SensusHarian.tanggal).label('end_date')
        ).first()
        
        print(f"📅 Periode Data: {date_range.start_date} s/d {date_range.end_date}")
        days_span = (date_range.end_date - date_range.start_date).days + 1
        print(f"📅 Rentang Hari: {days_span:,} hari")
        
        # BOR Statistics
        print(f"\n🏥 STATISTIK BED OCCUPANCY RATE (BOR)")
        print("-" * 40)
        bor_stats = db.query(
            func.min(SensusHarian.bor).label('min_bor'),
            func.max(SensusHarian.bor).label('max_bor'),
            func.avg(SensusHarian.bor).label('avg_bor'),
            func.count().label('count')
        ).first()
        
        print(f"📊 BOR Minimum    : {bor_stats.min_bor:.1f}%")
        print(f"📊 BOR Maximum    : {bor_stats.max_bor:.1f}%")
        print(f"📊 BOR Rata-rata  : {bor_stats.avg_bor:.1f}%")
        
        # Capacity statistics
        print(f"\n🛏️  STATISTIK KAPASITAS TEMPAT TIDUR")
        print("-" * 40)
        capacity_stats = db.query(
            func.min(SensusHarian.tempat_tidur_tersedia).label('min_cap'),
            func.max(SensusHarian.tempat_tidur_tersedia).label('max_cap'),
            func.avg(SensusHarian.tempat_tidur_tersedia).label('avg_cap')
        ).first()
        
        print(f"🛏️  Kapasitas Min  : {capacity_stats.min_cap} tempat tidur")
        print(f"🛏️  Kapasitas Max  : {capacity_stats.max_cap} tempat tidur")
        print(f"🛏️  Kapasitas Avg  : {capacity_stats.avg_cap:.0f} tempat tidur")
        
        # Patient flow statistics
        print(f"\n👥 STATISTIK ALUR PASIEN")
        print("-" * 40)
        patient_stats = db.query(
            func.avg(SensusHarian.jml_pasien_awal).label('avg_awal'),
            func.avg(SensusHarian.jml_masuk).label('avg_masuk'),
            func.avg(SensusHarian.jml_keluar).label('avg_keluar'),
            func.sum(SensusHarian.jml_masuk).label('total_masuk'),
            func.sum(SensusHarian.jml_keluar).label('total_keluar')
        ).first()
        
        print(f"👥 Rata-rata Pasien Awal : {patient_stats.avg_awal:.0f} pasien/hari")
        print(f"➡️  Rata-rata Pasien Masuk: {patient_stats.avg_masuk:.0f} pasien/hari")
        print(f"⬅️  Rata-rata Pasien Keluar: {patient_stats.avg_keluar:.0f} pasien/hari")
        print(f"📊 Total Admissions: {patient_stats.total_masuk:,} pasien")
        print(f"📊 Total Discharges: {patient_stats.total_keluar:,} pasien")
        
        # Quality indicators
        print(f"\n🎯 INDIKATOR KUALITAS RUMAH SAKIT")
        print("-" * 40)
        quality_stats = db.query(
            func.avg(SensusHarian.los).label('avg_los'),
            func.avg(SensusHarian.bto).label('avg_bto'),
            func.avg(SensusHarian.toi).label('avg_toi')
        ).first()
        
        print(f"⏱️  Length of Stay (LOS) : {quality_stats.avg_los:.1f} hari")
        print(f"🔄 Bed Turnover (BTO)   : {quality_stats.avg_bto:.2f}")
        print(f"⌛ Turn Over Interval   : {quality_stats.avg_toi:.1f} hari")
        
        # Monthly breakdown for latest year
        print(f"\n📅 BREAKDOWN DATA PER BULAN (2024)")
        print("-" * 40)
        monthly_data = db.query(
            extract('month', SensusHarian.tanggal).label('month'),
            func.count().label('records'),
            func.avg(SensusHarian.bor).label('avg_bor')
        ).filter(
            extract('year', SensusHarian.tanggal) == 2024
        ).group_by(
            extract('month', SensusHarian.tanggal)
        ).order_by('month').all()
        
        month_names = [
            'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
        ]
        
        for row in monthly_data:
            month_name = month_names[int(row.month) - 1]
            print(f"📊 {month_name} 2024: {row.records:2d} hari, BOR avg {row.avg_bor:.1f}%")
        
        # Seasonal patterns
        print(f"\n🌟 POLA SEASONAL")
        print("-" * 40)
        seasonal_data = db.query(
            extract('month', SensusHarian.tanggal).label('month'),
            func.avg(SensusHarian.bor).label('avg_bor')
        ).group_by(
            extract('month', SensusHarian.tanggal)
        ).order_by('month').all()
        
        # Find highest and lowest BOR months
        max_bor_month = max(seasonal_data, key=lambda x: x.avg_bor)
        min_bor_month = min(seasonal_data, key=lambda x: x.avg_bor)
        
        max_month_name = month_names[int(max_bor_month.month) - 1]
        min_month_name = month_names[int(min_bor_month.month) - 1]
        
        print(f"📈 Bulan Tertinggi BOR: {max_month_name} ({max_bor_month.avg_bor:.1f}%)")
        print(f"📉 Bulan Terendah BOR : {min_month_name} ({min_bor_month.avg_bor:.1f}%)")
        
        # Weekend vs Weekday analysis
        print(f"\n📅 ANALISIS WEEKEND vs WEEKDAY")
        print("-" * 40)
        
        # Note: This would require more complex date functions, simplified for now
        weekend_sample = db.query(SensusHarian).limit(100).all()
        weekday_admissions = []
        weekend_admissions = []
        
        for record in weekend_sample:
            if record.tanggal.weekday() >= 5:  # Saturday=5, Sunday=6
                weekend_admissions.append(record.jml_masuk)
            else:
                weekday_admissions.append(record.jml_masuk)
        
        if weekday_admissions and weekend_admissions:
            avg_weekday = sum(weekday_admissions) / len(weekday_admissions)
            avg_weekend = sum(weekend_admissions) / len(weekend_admissions)
            print(f"📊 Rata-rata Masuk Weekday: {avg_weekday:.1f} pasien")
            print(f"📊 Rata-rata Masuk Weekend: {avg_weekend:.1f} pasien")
            print(f"📊 Weekend Effect: {((avg_weekend/avg_weekday - 1) * 100):+.1f}%")
        
        print(f"\n" + "=" * 60)
        print("✅ Data sensus realistis siap untuk analisis dan ML!")
        print("🚀 Backend: http://localhost:8000/docs")
        print("🌐 Frontend: http://localhost:5174")
        
    finally:
        db.close()

if __name__ == "__main__":
    get_data_summary()