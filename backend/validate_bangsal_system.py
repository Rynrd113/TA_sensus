#!/usr/bin/env python3
# backend/validate_bangsal_system.py
"""
Validate that the bangsal system is working correctly
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.session import SessionLocal
from models.bangsal import Bangsal, KamarBangsal
from schemas.bangsal import BangsalResponse
from sqlalchemy import func

def validate_bangsal_system():
    """Validate bangsal system components"""
    db = SessionLocal()
    
    try:
        print("🔄 Validating Bangsal Management System...")
        
        # Test 1: Check if bangsal table exists and has data
        print("\n1. Checking bangsal database...")
        bangsal_count = db.query(Bangsal).count()
        print(f"   ✅ Found {bangsal_count} bangsal in database")
        
        # Test 2: Get sample bangsal data
        print("\n2. Sample bangsal data:")
        sample_bangsal = db.query(Bangsal).limit(3).all()
        for bangsal in sample_bangsal:
            print(f"   • {bangsal.nama_bangsal} ({bangsal.kode_bangsal})")
            print(f"     - Kapasitas: {bangsal.kapasitas_total}")
            print(f"     - Terisi: {bangsal.tempat_tidur_terisi}")
            print(f"     - Tersedia: {bangsal.tempat_tidur_tersedia}")
            print(f"     - Okupansi: {bangsal.occupancy_rate:.1f}%")
            print(f"     - Departemen: {bangsal.departemen}")
            print(f"     - Jenis: {bangsal.jenis_bangsal}")
            print()
        
        # Test 3: Check room data
        print("3. Checking room data...")
        room_count = db.query(KamarBangsal).count()
        print(f"   ✅ Found {room_count} rooms in database")
        
        # Test 4: Sample room data
        sample_rooms = db.query(KamarBangsal).limit(5).all()
        print("   Sample rooms:")
        for room in sample_rooms:
            print(f"   • {room.nomor_kamar}: {room.kapasitas_kamar} beds, {room.tempat_tidur_terisi} occupied")
            print(f"     Available: {room.is_available}, Clean: {room.status_kebersihan}")
        
        # Test 5: Validate schema conversion
        print("\n4. Testing schema conversion...")
        first_bangsal = db.query(Bangsal).first()
        if first_bangsal:
            response_data = first_bangsal.to_dict()
            response_data['occupancy_rate'] = first_bangsal.occupancy_rate
            response_data['available_beds'] = first_bangsal.available_beds
            
            bangsal_response = BangsalResponse(**response_data)
            print(f"   ✅ Schema conversion successful for: {bangsal_response.nama_bangsal}")
            print(f"      Response ID: {bangsal_response.id}")
            print(f"      Occupancy Rate: {bangsal_response.occupancy_rate}")
            print(f"      Available Beds: {bangsal_response.available_beds}")
        
        # Test 6: Statistics calculation
        print("\n5. Testing statistics calculation...")
        from sqlalchemy import case
        
        stats = db.query(
            func.count(Bangsal.id).label('total_bangsal'),
            func.sum(case((Bangsal.is_active == True, Bangsal.kapasitas_total), else_=0)).label('total_capacity'),
            func.sum(case((Bangsal.is_active == True, Bangsal.tempat_tidur_terisi), else_=0)).label('total_occupied'),
            func.sum(case((Bangsal.is_active == True, Bangsal.tempat_tidur_tersedia), else_=0)).label('total_available')
        ).first()
        
        total_capacity = stats.total_capacity or 0
        total_occupied = stats.total_occupied or 0
        occupancy_rate = (total_occupied / total_capacity * 100) if total_capacity > 0 else 0
        
        print(f"   Total Bangsal: {stats.total_bangsal}")
        print(f"   Total Capacity: {total_capacity}")
        print(f"   Total Occupied: {total_occupied}")
        print(f"   Total Available: {stats.total_available}")
        print(f"   Overall Occupancy: {occupancy_rate:.1f}%")
        
        # Test 7: Emergency ready bangsal
        print("\n6. Emergency ready bangsal:")
        emergency_bangsal = db.query(Bangsal).filter(
            Bangsal.is_emergency_ready == True,
            Bangsal.is_active == True,
            Bangsal.tempat_tidur_tersedia > 0
        ).all()
        
        print(f"   Found {len(emergency_bangsal)} emergency-ready bangsal:")
        for bangsal in emergency_bangsal:
            print(f"   • {bangsal.nama_bangsal}: {bangsal.tempat_tidur_tersedia} beds available")
        
        # Test 8: Department breakdown
        print("\n7. Department breakdown:")
        departments = db.query(Bangsal.departemen).filter(
            Bangsal.departemen.isnot(None),
            Bangsal.is_active == True
        ).distinct().all()
        
        for dept in departments:
            dept_bangsal = db.query(Bangsal).filter(
                Bangsal.departemen == dept[0],
                Bangsal.is_active == True
            ).all()
            
            dept_capacity = sum(b.kapasitas_total for b in dept_bangsal)
            dept_occupied = sum(b.tempat_tidur_terisi for b in dept_bangsal)
            dept_occupancy = (dept_occupied / dept_capacity * 100) if dept_capacity > 0 else 0
            
            print(f"   • {dept[0]}: {len(dept_bangsal)} bangsal, {dept_occupancy:.1f}% occupancy")
        
        print("\n✅ Bangsal system validation completed successfully!")
        print("\n📊 System Summary:")
        print(f"   • Database connectivity: ✅ Working")
        print(f"   • Bangsal models: ✅ {bangsal_count} records")
        print(f"   • Room models: ✅ {room_count} records")
        print(f"   • Schema conversion: ✅ Working")
        print(f"   • Statistics calculation: ✅ Working")
        print(f"   • Emergency system: ✅ {len(emergency_bangsal)} ready")
        print(f"   • Overall occupancy: {occupancy_rate:.1f}%")
        
    except Exception as e:
        print(f"❌ Error in validation: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    validate_bangsal_system()