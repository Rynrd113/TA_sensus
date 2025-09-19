#!/usr/bin/env python3
# backend/scripts/create_sample_bangsal.py
"""
Script to create sample bangsal data for testing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.session import SessionLocal
from models.bangsal import Bangsal, KamarBangsal
from database.engine import engine
from models.sensus import Base
import json

def create_sample_bangsal():
    """Create sample bangsal data"""
    db = SessionLocal()
    try:
        # Check if bangsal data already exists
        existing = db.query(Bangsal).first()
        if existing:
            print("📊 Bangsal data already exists")
            return

        print("🔄 Creating sample bangsal data...")

        # Create bangsal data
        sample_bangsal = [
            {
                "nama_bangsal": "Bangsal Mawar",
                "kode_bangsal": "MW-001",
                "kapasitas_total": 20,
                "jumlah_kamar": 5,
                "tempat_tidur_tersedia": 15,
                "tempat_tidur_terisi": 5,
                "departemen": "Internal Medicine",
                "jenis_bangsal": "Kelas I",
                "kategori": "Rawat Inap",
                "lantai": 2,
                "gedung": "Gedung Utama",
                "lokasi_detail": "Lantai 2, Sayap Timur",
                "is_active": True,
                "is_emergency_ready": False,
                "kepala_bangsal": "Dr. Sarah Wijaya",
                "perawat_jaga": "Ns. Rina Sari",
                "dokter_penanggung_jawab": "Dr. Ahmad Rahman",
                "tarif_per_hari": 500000.0,
                "fasilitas": json.dumps({
                    "AC": True,
                    "TV": True,
                    "Kulkas": False,
                    "Kamar Mandi Dalam": True,
                    "WiFi": True
                }),
                "keterangan": "Bangsal untuk pasien kelas 1 dengan fasilitas lengkap"
            },
            {
                "nama_bangsal": "Bangsal Melati",
                "kode_bangsal": "ML-001",
                "kapasitas_total": 30,
                "jumlah_kamar": 6,
                "tempat_tidur_tersedia": 22,
                "tempat_tidur_terisi": 8,
                "departemen": "Surgery",
                "jenis_bangsal": "Kelas II",
                "kategori": "Rawat Inap",
                "lantai": 3,
                "gedung": "Gedung Utama",
                "lokasi_detail": "Lantai 3, Sayap Barat",
                "is_active": True,
                "is_emergency_ready": True,
                "kepala_bangsal": "Dr. Budi Santoso",
                "perawat_jaga": "Ns. Maya Indah",
                "dokter_penanggung_jawab": "Dr. Lisa Permata",
                "tarif_per_hari": 350000.0,
                "fasilitas": json.dumps({
                    "AC": True,
                    "TV": False,
                    "Kulkas": False,
                    "Kamar Mandi Dalam": False,
                    "WiFi": True
                }),
                "keterangan": "Bangsal bedah dengan kesiapan emergency"
            },
            {
                "nama_bangsal": "ICU Utama",
                "kode_bangsal": "ICU-01",
                "kapasitas_total": 12,
                "jumlah_kamar": 12,
                "tempat_tidur_tersedia": 3,
                "tempat_tidur_terisi": 9,
                "departemen": "Critical Care",
                "jenis_bangsal": "ICU",
                "kategori": "Intensive Care",
                "lantai": 4,
                "gedung": "Gedung Utama",
                "lokasi_detail": "Lantai 4, Unit ICU",
                "is_active": True,
                "is_emergency_ready": True,
                "kepala_bangsal": "Dr. Indra Kusuma",
                "perawat_jaga": "Ns. Dewi Lestari",
                "dokter_penanggung_jawab": "Dr. Robert Tan",
                "tarif_per_hari": 1500000.0,
                "fasilitas": json.dumps({
                    "Ventilator": True,
                    "Cardiac Monitor": True,
                    "Defibrillator": True,
                    "Infusion Pump": True,
                    "Central Gas": True
                }),
                "keterangan": "Unit perawatan intensif dengan peralatan canggih"
            },
            {
                "nama_bangsal": "Bangsal Cempaka",
                "kode_bangsal": "CP-001",
                "kapasitas_total": 25,
                "jumlah_kamar": 8,
                "tempat_tidur_tersedia": 20,
                "tempat_tidur_terisi": 5,
                "departemen": "Pediatrics",
                "jenis_bangsal": "Kelas III",
                "kategori": "Rawat Inap",
                "lantai": 1,
                "gedung": "Gedung Anak",
                "lokasi_detail": "Lantai 1, Gedung Khusus Anak",
                "is_active": True,
                "is_emergency_ready": False,
                "kepala_bangsal": "Dr. Siti Nurjannah",
                "perawat_jaga": "Ns. Ani Suryani",
                "dokter_penanggung_jawab": "Dr. Teguh Prasetyo",
                "tarif_per_hari": 250000.0,
                "fasilitas": json.dumps({
                    "AC": False,
                    "TV": False,
                    "Kulkas": False,
                    "Kamar Mandi Dalam": False,
                    "WiFi": False
                }),
                "keterangan": "Bangsal anak dengan tarif terjangkau"
            },
            {
                "nama_bangsal": "Bangsal VIP Anggrek",
                "kode_bangsal": "VIP-01",
                "kapasitas_total": 10,
                "jumlah_kamar": 10,
                "tempat_tidur_tersedia": 7,
                "tempat_tidur_terisi": 3,
                "departemen": "Internal Medicine",
                "jenis_bangsal": "VIP",
                "kategori": "Rawat Inap",
                "lantai": 5,
                "gedung": "Gedung Utama",
                "lokasi_detail": "Lantai 5, Suite VIP",
                "is_active": True,
                "is_emergency_ready": True,
                "kepala_bangsal": "Dr. Kartika Sari",
                "perawat_jaga": "Ns. Putri Handayani",
                "dokter_penanggung_jawab": "Dr. Vincent Halim",
                "tarif_per_hari": 1200000.0,
                "fasilitas": json.dumps({
                    "AC": True,
                    "TV": True,
                    "Kulkas": True,
                    "Kamar Mandi Dalam": True,
                    "WiFi": True,
                    "Sofa": True,
                    "Meja Kerja": True
                }),
                "keterangan": "Suite VIP dengan fasilitas mewah"
            },
            {
                "nama_bangsal": "NICU",
                "kode_bangsal": "NICU-1",
                "kapasitas_total": 8,
                "jumlah_kamar": 1,
                "tempat_tidur_tersedia": 2,
                "tempat_tidur_terisi": 6,
                "departemen": "Neonatology",
                "jenis_bangsal": "NICU",
                "kategori": "Neonatal Intensive Care",
                "lantai": 3,
                "gedung": "Gedung Anak",
                "lokasi_detail": "Lantai 3, Unit NICU",
                "is_active": True,
                "is_emergency_ready": True,
                "kepala_bangsal": "Dr. Maria Stefani",
                "perawat_jaga": "Ns. Ratna Wulan",
                "dokter_penanggung_jawab": "Dr. Kevin Sutanto",
                "tarif_per_hari": 2000000.0,
                "fasilitas": json.dumps({
                    "Incubator": True,
                    "Ventilator": True,
                    "Phototherapy": True,
                    "Infusion Pump": True,
                    "Central Monitoring": True
                }),
                "keterangan": "Unit perawatan intensif neonatal"
            }
        ]

        # Create bangsal records
        for bangsal_data in sample_bangsal:
            bangsal = Bangsal(**bangsal_data)
            db.add(bangsal)

        db.commit()
        print(f"✅ Created {len(sample_bangsal)} sample bangsal records!")

        # Create sample rooms for some bangsal
        print("🔄 Creating sample rooms...")
        
        # Get created bangsal
        bangsal_list = db.query(Bangsal).all()
        
        room_data = []
        for bangsal in bangsal_list[:3]:  # Create rooms for first 3 bangsal
            if bangsal.kode_bangsal == "MW-001":  # Bangsal Mawar
                rooms = [
                    {"nomor_kamar": "MW-201", "nama_kamar": "Kamar Mawar 1", "kapasitas_kamar": 4, "tempat_tidur_terisi": 1},
                    {"nomor_kamar": "MW-202", "nama_kamar": "Kamar Mawar 2", "kapasitas_kamar": 4, "tempat_tidur_terisi": 2},
                    {"nomor_kamar": "MW-203", "nama_kamar": "Kamar Mawar 3", "kapasitas_kamar": 4, "tempat_tidur_terisi": 0},
                    {"nomor_kamar": "MW-204", "nama_kamar": "Kamar Mawar 4", "kapasitas_kamar": 4, "tempat_tidur_terisi": 1},
                    {"nomor_kamar": "MW-205", "nama_kamar": "Kamar Mawar 5", "kapasitas_kamar": 4, "tempat_tidur_terisi": 1}
                ]
            elif bangsal.kode_bangsal == "ML-001":  # Bangsal Melati
                rooms = [
                    {"nomor_kamar": "ML-301", "nama_kamar": "Kamar Melati 1", "kapasitas_kamar": 5, "tempat_tidur_terisi": 3},
                    {"nomor_kamar": "ML-302", "nama_kamar": "Kamar Melati 2", "kapasitas_kamar": 5, "tempat_tidur_terisi": 2},
                    {"nomor_kamar": "ML-303", "nama_kamar": "Kamar Melati 3", "kapasitas_kamar": 5, "tempat_tidur_terisi": 1},
                    {"nomor_kamar": "ML-304", "nama_kamar": "Kamar Melati 4", "kapasitas_kamar": 5, "tempat_tidur_terisi": 1},
                    {"nomor_kamar": "ML-305", "nama_kamar": "Kamar Melati 5", "kapasitas_kamar": 5, "tempat_tidur_terisi": 1},
                    {"nomor_kamar": "ML-306", "nama_kamar": "Kamar Melati 6", "kapasitas_kamar": 5, "tempat_tidur_terisi": 0}
                ]
            elif bangsal.kode_bangsal == "ICU-01":  # ICU
                rooms = [
                    {"nomor_kamar": f"ICU-{i:02d}", "nama_kamar": f"ICU Bed {i}", "kapasitas_kamar": 1, 
                     "tempat_tidur_terisi": 1 if i <= 9 else 0} 
                    for i in range(1, 13)
                ]

            # Create room records
            for room_info in rooms:
                room = KamarBangsal(
                    bangsal_id=bangsal.id,
                    nomor_kamar=room_info["nomor_kamar"],
                    nama_kamar=room_info["nama_kamar"],
                    kapasitas_kamar=room_info["kapasitas_kamar"],
                    tempat_tidur_terisi=room_info["tempat_tidur_terisi"],
                    jenis_kamar="Standard",
                    is_active=True,
                    is_maintenance=False,
                    status_kebersihan="Bersih"
                )
                db.add(room)
                room_data.append(room)

        db.commit()
        print(f"✅ Created {len(room_data)} sample room records!")

        print("\n📊 Sample Bangsal Data Summary:")
        for bangsal in bangsal_list:
            print(f"  • {bangsal.nama_bangsal} ({bangsal.kode_bangsal})")
            print(f"    - Kapasitas: {bangsal.kapasitas_total} beds")
            print(f"    - Tersedia: {bangsal.tempat_tidur_tersedia} beds")
            print(f"    - Okupansi: {bangsal.occupancy_rate:.1f}%")
            print(f"    - Departemen: {bangsal.departemen}")
            print(f"    - Jenis: {bangsal.jenis_bangsal}")
            print()

    except Exception as e:
        print(f"❌ Error creating sample data: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    # Ensure tables are created
    Base.metadata.create_all(bind=engine)
    print("🔄 Database tables ensured...")
    
    # Create sample data
    create_sample_bangsal()
    print("✅ Sample bangsal data creation completed!")