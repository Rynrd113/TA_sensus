#!/usr/bin/env python3
# backend/test_bangsal_api.py
"""
Test script for bangsal API functionality
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.bangsal_service import BangsalService
from schemas.bangsal import BangsalCreate, BangsalUpdate, CapacityUpdate
from database.session import SessionLocal
import json
import asyncio

async def test_bangsal_service():
    """Test bangsal service functionality"""
    db = SessionLocal()
    service = BangsalService(db)
    
    try:
        print("🔄 Testing Bangsal Management System...")
        
        # Test 1: Get all bangsal
        print("\n1. Getting all bangsal...")
        bangsal_list = await service.get_bangsal_list(page=1, per_page=10)
        print(f"   Found {bangsal_list.total} bangsal")
        for bangsal in bangsal_list.bangsal[:3]:  # Show first 3
            print(f"   • {bangsal.nama_bangsal} ({bangsal.kode_bangsal})")
            print(f"     - Kapasitas: {bangsal.kapasitas_total}, Tersedia: {bangsal.tempat_tidur_tersedia}")
            print(f"     - Okupansi: {bangsal.occupancy_rate:.1f}%")
        
        # Test 2: Get specific bangsal
        print("\n2. Getting bangsal by ID...")
        bangsal = await service.get_bangsal(1)
        if bangsal:
            print(f"   ✅ Found: {bangsal.nama_bangsal}")
            print(f"      Kode: {bangsal.kode_bangsal}")
            print(f"      Departemen: {bangsal.departemen}")
            print(f"      Jenis: {bangsal.jenis_bangsal}")
            print(f"      Kapasitas Total: {bangsal.kapasitas_total}")
            print(f"      Terisi: {bangsal.tempat_tidur_terisi}")
            print(f"      Tersedia: {bangsal.tempat_tidur_tersedia}")
        
        # Test 3: Get bangsal by code
        print("\n3. Getting bangsal by kode...")
        bangsal = await service.get_bangsal_by_kode("MW-001")
        if bangsal:
            print(f"   ✅ Found: {bangsal.nama_bangsal}")
        
        # Test 4: Get emergency ready bangsal
        print("\n4. Getting emergency ready bangsal...")
        emergency_bangsal = await service.get_emergency_ready_bangsal()
        print(f"   Found {len(emergency_bangsal)} emergency-ready bangsal:")
        for bangsal in emergency_bangsal:
            print(f"   • {bangsal.nama_bangsal} - {bangsal.tempat_tidur_tersedia} beds available")
        
        # Test 5: Get available bangsal
        print("\n5. Getting bangsal with available beds...")
        available_bangsal = await service.get_available_bangsal(min_beds=2)
        print(f"   Found {len(available_bangsal)} bangsal with 2+ beds available:")
        for bangsal in available_bangsal[:3]:
            print(f"   • {bangsal.nama_bangsal} - {bangsal.tempat_tidur_tersedia} beds")
        
        # Test 6: Get occupancy statistics
        print("\n6. Getting occupancy statistics...")
        stats = await service.get_occupancy_statistics()
        print(f"   Total Bangsal: {stats.total_bangsal}")
        print(f"   Active Bangsal: {stats.active_bangsal}")
        print(f"   Total Capacity: {stats.total_capacity}")
        print(f"   Total Occupied: {stats.total_occupied}")
        print(f"   Total Available: {stats.total_available}")
        print(f"   Overall Occupancy: {stats.overall_occupancy_rate:.1f}%")
        print(f"   Emergency Ready: {stats.emergency_ready_bangsal}")
        
        # Test 7: Get department statistics
        print("\n7. Getting department statistics...")
        dept_stats = await service.get_department_statistics()
        print("   Department breakdown:")
        for dept in dept_stats:
            print(f"   • {dept['departemen']}: {dept['occupancy_rate']:.1f}% occupancy")
            print(f"     - Bangsal: {dept['total_bangsal']}, Capacity: {dept['total_capacity']}")
        
        # Test 8: Update bed capacity
        print("\n8. Testing bed capacity update...")
        capacity_update = CapacityUpdate(tempat_tidur_terisi=12)
        updated_bangsal = await service.update_bed_capacity(1, capacity_update)
        if updated_bangsal:
            print(f"   ✅ Updated {updated_bangsal.nama_bangsal}")
            print(f"      New occupancy: {updated_bangsal.occupancy_rate:.1f}%")
        
        # Test 9: Get rooms for bangsal
        print("\n9. Getting rooms for bangsal...")
        rooms = await service.get_bangsal_rooms(1)  # Bangsal Mawar
        print(f"   Found {len(rooms)} rooms:")
        for room in rooms[:3]:  # Show first 3
            print(f"   • {room.nomor_kamar}: {room.kapasitas_kamar} beds, {room.tempat_tidur_terisi} occupied")
            print(f"     Available: {room.is_available}, Beds: {room.available_beds}")
        
        # Test 10: Get available rooms
        print("\n10. Getting available rooms...")
        available_rooms = await service.get_available_rooms(1)
        print(f"    Found {len(available_rooms)} available rooms:")
        for room in available_rooms:
            print(f"    • {room.nomor_kamar}: {room.available_beds} beds available")
        
        # Test 11: Create new bangsal
        print("\n11. Testing bangsal creation...")
        new_bangsal_data = BangsalCreate(
            nama_bangsal="Bangsal Test API",
            kode_bangsal="TEST-01",
            kapasitas_total=15,
            jumlah_kamar=3,
            departemen="Internal Medicine",
            jenis_bangsal="Kelas II",
            kategori="Rawat Inap",
            lantai=2,
            gedung="Gedung Test",
            is_active=True,
            is_emergency_ready=False,
            fasilitas=json.dumps({"AC": True, "WiFi": True}),
            keterangan="Bangsal untuk testing API"
        )
        
        new_bangsal = await service.create_bangsal(new_bangsal_data, created_by=1)
        if new_bangsal:
            print(f"   ✅ Created new bangsal: {new_bangsal.nama_bangsal}")
            print(f"      ID: {new_bangsal.id}, Kode: {new_bangsal.kode_bangsal}")
            
            # Test 12: Update the new bangsal
            print("\n12. Testing bangsal update...")
            update_data = BangsalUpdate(
                keterangan="Updated via API test",
                tarif_per_hari=400000.0
            )
            updated = await service.update_bangsal(new_bangsal.id, update_data, updated_by=1)
            if updated:
                print(f"   ✅ Updated bangsal: {updated.keterangan}")
                print(f"      Tarif: Rp {updated.tarif_per_hari:,.0f}")
            
            # Test 13: Delete the test bangsal
            print("\n13. Testing bangsal deletion...")
            deleted = await service.delete_bangsal(new_bangsal.id, hard_delete=False)
            if deleted:
                print(f"   ✅ Soft deleted test bangsal")
        
        print("\n✅ All bangsal tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error in bangsal test: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_bangsal_service())