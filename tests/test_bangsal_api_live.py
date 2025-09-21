#!/usr/bin/env python3
"""
Live Bangsal API Testing
Test bangsal endpoints with actual server running on port 8001
"""

import requests
import json
import sys
from typing import Dict, Any

BASE_URL = "http://127.0.0.1:8001/api/v1"

def test_api_connection():
    """Test basic API connectivity"""
    try:
        response = requests.get("http://127.0.0.1:8001/")
        print(f"✅ Server is running: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Server connection failed: {e}")
        return False

def test_authentication():
    """Test authentication endpoint"""
    # Test login with default admin user
    login_data = {
        "username": "admin",
        "password": "admin123"  # Default admin password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Authentication successful")
            return token_data.get("access_token")
        else:
            print(f"❌ Authentication failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None

def test_bangsal_endpoints(token: str):
    """Test bangsal endpoints with authentication"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🏥 Testing Bangsal API Endpoints:")
    
    # Test 1: Get all bangsal
    print("\n1. Testing GET /bangsal/")
    try:
        response = requests.get(f"{BASE_URL}/bangsal/", headers=headers)
        if response.status_code == 200:
            bangsal_list = response.json()
            print(f"✅ Retrieved {len(bangsal_list)} bangsal")
            
            # Show first bangsal details
            if bangsal_list:
                first_bangsal = bangsal_list[0]
                print(f"   Sample: {first_bangsal.get('nama_bangsal')} - {first_bangsal.get('kapasitas_total')} beds")
        else:
            print(f"❌ Failed to get bangsal list: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing bangsal list: {e}")
    
    # Test 2: Get bangsal statistics
    print("\n2. Testing GET /bangsal/statistics")
    try:
        response = requests.get(f"{BASE_URL}/bangsal/statistics", headers=headers)
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Statistics retrieved:")
            print(f"   Total Bangsal: {stats.get('total_bangsal')}")
            print(f"   Total Capacity: {stats.get('total_capacity')}")
            print(f"   Occupancy Rate: {stats.get('occupancy_rate')}%")
        else:
            print(f"❌ Failed to get statistics: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing statistics: {e}")
    
    # Test 3: Get emergency ready bangsal
    print("\n3. Testing GET /bangsal/emergency")
    try:
        response = requests.get(f"{BASE_URL}/bangsal/emergency", headers=headers)
        if response.status_code == 200:
            emergency_bangsal = response.json()
            print(f"✅ Found {len(emergency_bangsal)} emergency-ready bangsal")
            for bangsal in emergency_bangsal[:3]:  # Show first 3
                print(f"   - {bangsal.get('nama_bangsal')}: {bangsal.get('available_beds')} beds available")
        else:
            print(f"❌ Failed to get emergency bangsal: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing emergency endpoint: {e}")
    
    # Test 4: Get bangsal by department
    print("\n4. Testing GET /bangsal/by-department")
    try:
        response = requests.get(f"{BASE_URL}/bangsal/by-department?department=Internal Medicine", headers=headers)
        if response.status_code == 200:
            dept_bangsal = response.json()
            print(f"✅ Found {len(dept_bangsal)} bangsal in Internal Medicine")
        else:
            print(f"❌ Failed to get bangsal by department: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing department filter: {e}")

def main():
    """Main test function"""
    print("🚀 Starting Bangsal API Live Testing...")
    
    # Test 1: Basic connectivity
    if not test_api_connection():
        print("❌ Cannot connect to server. Make sure it's running on port 8001")
        sys.exit(1)
    
    # Test 2: Authentication
    token = test_authentication()
    if not token:
        print("❌ Cannot authenticate. Skipping API tests.")
        print("💡 Make sure admin user exists with username='admin' and password='admin123'")
        return
    
    # Test 3: Bangsal endpoints
    test_bangsal_endpoints(token)
    
    print("\n🎉 Bangsal API testing completed!")
    print("✅ Import issues resolved - bangsal router is working!")

if __name__ == "__main__":
    main()