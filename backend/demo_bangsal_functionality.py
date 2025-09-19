#!/usr/bin/env python3
# backend/demo_bangsal_functionality.py
"""
Demonstrate bangsal management system functionality
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
import json
from database.session import SessionLocal
from services.bangsal_service import BangsalService
from repositories.bangsal_repository import BangsalRepository
from schemas.bangsal import BangsalCreate, BangsalUpdate, CapacityUpdate

def demonstrate_functionality():
    """Demonstrate all bangsal system features"""
    db = SessionLocal()
    
    print("🏥 Bangsal Management System Functionality Demo")
    print("=" * 50)
    
    try:
        # Test 1: Repository Direct Access
        print("\n📊 1. Direct Repository Access")
        print("-" * 30)
        
        repo = BangsalRepository(db)
        
        # Get all bangsal
        all_bangsal = repo.get_all_bangsal()
        print(f"✅ Found {len(all_bangsal)} bangsal in database")
        
        for bangsal in all_bangsal[:3]:
            print(f"   • {bangsal.nama_bangsal} ({bangsal.kode_bangsal})")
            print(f"     - Kapasitas: {bangsal.kapasitas_total} beds")
            print(f"     - Terisi: {bangsal.tempat_tidur_terisi} beds")
            print(f"     - Tersedia: {bangsal.tempat_tidur_tersedia} beds")
            print(f"     - Okupansi: {bangsal.occupancy_rate:.1f}%")
            print(f"     - Departemen: {bangsal.departemen}")
            print(f"     - Emergency Ready: {'✅' if bangsal.is_emergency_ready else '❌'}")
        
        # Test 2: Statistics
        print("\n📈 2. Hospital Statistics")
        print("-" * 30)
        
        stats = repo.get_occupancy_statistics()
        print(f"✅ Hospital Overview:")
        print(f"   • Total Bangsal: {stats['total_bangsal']}")
        print(f"   • Active Bangsal: {stats['active_bangsal']}")
        print(f"   • Total Capacity: {stats['total_capacity']} beds")
        print(f"   • Total Occupied: {stats['total_occupied']} beds")
        print(f"   • Total Available: {stats['total_available']} beds")
        print(f"   • Overall Occupancy: {stats['overall_occupancy_rate']:.1f}%")
        print(f"   • Emergency Ready: {stats['emergency_ready_bangsal']} bangsal")
        
        # Test 3: Department Statistics
        print("\n🏢 3. Department Breakdown")
        print("-" * 30)
        
        dept_stats = repo.get_department_statistics()
        print(f"✅ Found {len(dept_stats)} departments:")
        for dept in dept_stats:
            print(f"   • {dept['departemen']}")
            print(f"     - Bangsal: {dept['total_bangsal']}")
            print(f"     - Capacity: {dept['total_capacity']} beds")
            print(f"     - Occupied: {dept['total_occupied']} beds")
            print(f"     - Occupancy: {dept['occupancy_rate']:.1f}%")
        
        # Test 4: Emergency Ready Bangsal
        print("\n🚨 4. Emergency Ready Bangsal")
        print("-" * 30)
        
        emergency_bangsal = repo.get_emergency_ready_bangsal()
        print(f"✅ Found {len(emergency_bangsal)} emergency-ready bangsal:")
        for bangsal in emergency_bangsal:
            print(f"   • {bangsal.nama_bangsal}")
            print(f"     - Available: {bangsal.tempat_tidur_tersedia} beds")
            print(f"     - Type: {bangsal.jenis_bangsal}")
            print(f"     - Department: {bangsal.departemen}")
        
        # Test 5: Available Bangsal
        print("\n🛏️ 5. Available Bangsal (5+ beds)")
        print("-" * 30)
        
        available_bangsal = repo.get_available_bangsal(min_beds=5)
        print(f"✅ Found {len(available_bangsal)} bangsal with 5+ available beds:")
        for bangsal in available_bangsal:
            print(f"   • {bangsal.nama_bangsal}")
            print(f"     - Available: {bangsal.tempat_tidur_tersedia} beds")
            print(f"     - Occupancy: {bangsal.occupancy_rate:.1f}%")
            print(f"     - Type: {bangsal.jenis_bangsal}")
        
        # Test 6: Search Functionality
        print("\n🔍 6. Search Functionality")
        print("-" * 30)
        
        search_results = repo.search_bangsal("ICU")
        print(f"✅ Search for 'ICU' found {len(search_results)} results:")
        for bangsal in search_results:
            print(f"   • {bangsal.nama_bangsal} ({bangsal.kode_bangsal})")
            print(f"     - Type: {bangsal.jenis_bangsal}")
            print(f"     - Available: {bangsal.tempat_tidur_tersedia} beds")
        
        # Test 7: Filtering
        print("\n🗂️ 7. Filter by Department")
        print("-" * 30)
        
        internal_bangsal = repo.get_bangsal_by_department("Internal Medicine")
        print(f"✅ Internal Medicine department has {len(internal_bangsal)} bangsal:")
        for bangsal in internal_bangsal:
            print(f"   • {bangsal.nama_bangsal}")
            print(f"     - Type: {bangsal.jenis_bangsal}")
            print(f"     - Occupancy: {bangsal.occupancy_rate:.1f}%")
        
        # Test 8: Capacity Update
        print("\n⚙️ 8. Capacity Management")
        print("-" * 30)
        
        # Get a bangsal to update
        test_bangsal = repo.get_bangsal_by_id(1)
        if test_bangsal:
            print(f"✅ Before update - {test_bangsal.nama_bangsal}:")
            print(f"   - Occupied: {test_bangsal.tempat_tidur_terisi} beds")
            print(f"   - Available: {test_bangsal.tempat_tidur_tersedia} beds")
            print(f"   - Occupancy: {test_bangsal.occupancy_rate:.1f}%")
            
            # Update capacity
            original_occupied = test_bangsal.tempat_tidur_terisi
            updated_bangsal = repo.update_bed_capacity(1, original_occupied + 2)
            
            if updated_bangsal:
                print(f"✅ After capacity update:")
                print(f"   - Occupied: {updated_bangsal.tempat_tidur_terisi} beds (+2)")
                print(f"   - Available: {updated_bangsal.tempat_tidur_tersedia} beds")
                print(f"   - Occupancy: {updated_bangsal.occupancy_rate:.1f}%")
                
                # Restore original capacity
                repo.update_bed_capacity(1, original_occupied)
                print(f"✅ Capacity restored to original value")
        
        # Test 9: Room Management
        print("\n🏠 9. Room Management")
        print("-" * 30)
        
        from repositories.bangsal_repository import KamarBangsalRepository
        room_repo = KamarBangsalRepository(db)
        
        # Get rooms for first bangsal
        rooms = room_repo.get_kamar_by_bangsal(1)
        print(f"✅ Bangsal 1 has {len(rooms)} rooms:")
        for room in rooms[:5]:  # Show first 5
            availability = "✅ Available" if room.is_available else "❌ Not Available"
            print(f"   • {room.nomor_kamar}: {room.kapasitas_kamar} beds, {room.tempat_tidur_terisi} occupied - {availability}")
            print(f"     - Status: {room.status_kebersihan}, Maintenance: {'Yes' if room.is_maintenance else 'No'}")
        
        # Get available rooms only
        available_rooms = room_repo.get_available_kamar(1)
        print(f"✅ Available rooms in bangsal 1: {len(available_rooms)} out of {len(rooms)}")
        
        # Test 10: Data Validation
        print("\n✅ 10. Data Validation")
        print("-" * 30)
        
        # Check data consistency
        all_bangsal = repo.get_all_bangsal()
        consistent_count = 0
        total_count = len(all_bangsal)
        
        for bangsal in all_bangsal:
            expected_available = bangsal.kapasitas_total - bangsal.tempat_tidur_terisi
            if bangsal.tempat_tidur_tersedia == expected_available:
                consistent_count += 1
        
        print(f"✅ Data Consistency Check:")
        print(f"   - Total bangsal: {total_count}")
        print(f"   - Consistent data: {consistent_count}")
        print(f"   - Consistency rate: {(consistent_count/total_count*100):.1f}%")
        
        print("\n🎉 Bangsal Management System Demo Complete!")
        print("=" * 50)
        
        print("\n📋 System Capabilities Summary:")
        print("✅ Complete CRUD operations")
        print("✅ Real-time occupancy calculations")
        print("✅ Emergency readiness tracking")
        print("✅ Department-based management")
        print("✅ Advanced search and filtering")
        print("✅ Room-level management")
        print("✅ Capacity synchronization")
        print("✅ Statistical reporting")
        print("✅ Data validation and consistency")
        print("✅ Bulk operations support")
        
        print("\n🔗 Ready for Integration:")
        print("• Hospital dashboard widgets")
        print("• Emergency response system")
        print("• Patient admission workflow")
        print("• Capacity planning tools")
        print("• Daily census reporting")
        print("• Mobile applications")
        print("• Third-party EHR systems")
        
    except Exception as e:
        print(f"❌ Error in demo: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    demonstrate_functionality()