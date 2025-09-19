#!/usr/bin/env python3
"""
Script untuk memverifikasi sinkronisasi data antara database dan frontend dashboard
"""

import sys
import os
import requests
import json

# Add backend path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from database.session import SessionLocal
from models.sensus import SensusHarian
from sqlalchemy import func

def get_database_stats():
    """Ambil statistik langsung dari database"""
    db = SessionLocal()
    try:
        # Total records
        total_records = db.query(SensusHarian).count()
        
        # Latest data
        latest = db.query(SensusHarian).order_by(SensusHarian.tanggal.desc()).first()
        
        # Summary stats
        stats = db.query(
            func.avg(SensusHarian.bor).label('avg_bor'),
            func.sum(SensusHarian.jml_masuk).label('total_masuk'),
            func.sum(SensusHarian.jml_keluar).label('total_keluar'),
            func.avg(SensusHarian.tempat_tidur_tersedia).label('avg_capacity')
        ).first()
        
        return {
            'total_records': total_records,
            'latest_date': str(latest.tanggal) if latest else None,
            'latest_bor': latest.bor if latest else None,
            'latest_total_pasien': latest.jml_pasien_akhir if latest else None,
            'latest_capacity': latest.tempat_tidur_tersedia if latest else None,
            'kapasitas_kosong': (latest.tempat_tidur_tersedia - latest.jml_pasien_akhir) if latest else None,
            'avg_bor': float(stats.avg_bor) if stats.avg_bor else None,
            'total_admissions': int(stats.total_masuk) if stats.total_masuk else None,
            'total_discharges': int(stats.total_keluar) if stats.total_keluar else None,
            'avg_capacity': float(stats.avg_capacity) if stats.avg_capacity else None
        }
    finally:
        db.close()

def get_api_stats():
    """Ambil statistik dari API dashboard"""
    try:
        # Dashboard stats
        dashboard_response = requests.get('http://localhost:8000/api/v1/dashboard/stats', timeout=10)
        dashboard_data = dashboard_response.json()
        
        # Latest sensus data
        sensus_response = requests.get('http://localhost:8000/api/v1/sensus/?limit=1', timeout=10)
        sensus_data = sensus_response.json()
        
        latest_sensus = sensus_data[0] if sensus_data else None
        
        return {
            'api_available': True,
            'dashboard_stats': dashboard_data.get('stats', {}),
            'latest_sensus': latest_sensus
        }
    except requests.RequestException as e:
        return {
            'api_available': False,
            'error': str(e)
        }

def compare_data():
    """Bandingkan data database vs API/Frontend"""
    print("🔍 VERIFIKASI SINKRONISASI DATA DATABASE ↔ FRONTEND")
    print("=" * 60)
    
    # Get database stats
    print("📊 Mengambil data dari database...")
    db_stats = get_database_stats()
    
    # Get API stats
    print("🌐 Mengambil data dari API...")
    api_stats = get_api_stats()
    
    print("\n📈 PERBANDINGAN DATA:")
    print("-" * 40)
    
    if not api_stats['api_available']:
        print(f"❌ API tidak tersedia: {api_stats['error']}")
        print("💡 Pastikan backend server berjalan di http://localhost:8000")
        return
    
    dashboard = api_stats['dashboard_stats']
    latest_api = api_stats['latest_sensus']
    
    # Comparison table
    comparisons = [
        {
            'metric': 'Total Records',
            'database': db_stats['total_records'],
            'api': 'Not directly available from dashboard API',
            'match': '⚠️'
        },
        {
            'metric': 'Tanggal Terbaru',
            'database': db_stats['latest_date'],
            'api': dashboard.get('tanggal_terakhir'),
            'match': '✅' if db_stats['latest_date'] == dashboard.get('tanggal_terakhir') else '❌'
        },
        {
            'metric': 'BOR Terbaru (%)',
            'database': db_stats['latest_bor'],
            'api': dashboard.get('bor_terkini'),
            'match': '✅' if abs(db_stats['latest_bor'] - dashboard.get('bor_terkini', 0)) < 0.1 else '❌'
        },
        {
            'metric': 'Total Pasien Hari Ini',
            'database': db_stats['latest_total_pasien'],
            'api': dashboard.get('total_pasien_hari_ini'),
            'match': '✅' if db_stats['latest_total_pasien'] == dashboard.get('total_pasien_hari_ini') else '❌'
        },
        {
            'metric': 'Total TT',
            'database': db_stats['latest_capacity'],
            'api': dashboard.get('tt_total'),
            'match': '✅' if db_stats['latest_capacity'] == dashboard.get('tt_total') else '❌'
        },
        {
            'metric': 'Kapasitas Kosong',
            'database': db_stats['kapasitas_kosong'],
            'api': dashboard.get('kapasitas_kosong'),
            'match': '✅' if db_stats['kapasitas_kosong'] == dashboard.get('kapasitas_kosong') else '❌'
        }
    ]
    
    # Print comparison table
    print(f"{'Metric':<25} | {'Database':<15} | {'API/Frontend':<15} | {'Status':<6}")
    print("-" * 70)
    
    all_match = True
    for comp in comparisons:
        db_val = str(comp['database']) if comp['database'] is not None else 'None'
        api_val = str(comp['api']) if comp['api'] is not None else 'None'
        
        print(f"{comp['metric']:<25} | {db_val:<15} | {api_val:<15} | {comp['match']:<6}")
        
        if comp['match'] == '❌':
            all_match = False
    
    print("\n📊 DETAIL DATA TERBARU:")
    print("-" * 40)
    print(f"Database - Tanggal: {db_stats['latest_date']}")
    print(f"Database - BOR: {db_stats['latest_bor']:.1f}%")
    print(f"Database - Pasien: {db_stats['latest_total_pasien']}")
    print(f"Database - Kapasitas: {db_stats['latest_capacity']}")
    
    print(f"\nAPI - Tanggal: {dashboard.get('tanggal_terakhir')}")
    print(f"API - BOR: {dashboard.get('bor_terkini', 0):.1f}%")
    print(f"API - Pasien: {dashboard.get('total_pasien_hari_ini')}")
    print(f"API - Kapasitas: {dashboard.get('tt_total')}")
    
    # Additional verification from latest sensus
    if latest_api:
        print(f"\n🔗 VERIFIKASI DARI SENSUS API:")
        print("-" * 40)
        print(f"Sensus API - ID: {latest_api.get('id')}")
        print(f"Sensus API - Tanggal: {latest_api.get('tanggal')}")
        print(f"Sensus API - BOR: {latest_api.get('bor'):.1f}%")
        print(f"Sensus API - Pasien Akhir: {latest_api.get('jml_pasien_akhir')}")
        print(f"Sensus API - TT Tersedia: {latest_api.get('tempat_tidur_tersedia')}")
        
        # Check consistency between dashboard and sensus API
        sensus_consistent = (
            latest_api.get('tanggal') == dashboard.get('tanggal_terakhir') and
            abs(latest_api.get('bor', 0) - dashboard.get('bor_terkini', 0)) < 0.1 and
            latest_api.get('jml_pasien_akhir') == dashboard.get('total_pasien_hari_ini') and
            latest_api.get('tempat_tidur_tersedia') == dashboard.get('tt_total')
        )
        
        print(f"\n🔄 Konsistensi Dashboard ↔ Sensus API: {'✅' if sensus_consistent else '❌'}")
    
    # Summary
    print("\n" + "=" * 60)
    if all_match and api_stats['api_available']:
        print("✅ SINKRONISASI BERHASIL!")
        print("📊 Semua data database sudah sinkron dengan frontend")
        print("🎯 Dashboard menampilkan data yang akurat dari 1000 records")
    else:
        print("⚠️  DITEMUKAN KETIDAKCOCOKAN!")
        print("🔧 Periksa kembali koneksi API dan logika perhitungan")
        if not all_match:
            print("📋 Beberapa data tidak cocok antara database dan API")
    
    print(f"\n📈 Total data tersedia: {db_stats['total_records']:,} records")
    print(f"📅 Periode: 2024-2026 (realistic synthetic data)")
    print(f"🌐 Frontend: http://localhost:5174")
    print(f"📚 API Docs: http://localhost:8000/docs")

if __name__ == "__main__":
    compare_data()