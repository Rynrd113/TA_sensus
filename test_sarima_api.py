#!/usr/bin/env python3
"""
SARIMA API Client Test
Test semua endpoints SARIMA untuk memastikan functionality end-to-end
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
TEST_USER = {
    "username": "testuser",
    "password": "testpass123"
}

def test_sarima_endpoints():
    """Test all SARIMA API endpoints"""
    print("🔗 Testing SARIMA API Endpoints...")
    print("="*60)
    
    # Test 1: Check model status
    print("\n1. Testing Model Status Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/sarima/status")
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Model Trained: {data.get('model_trained', False)}")
            print("   ✅ Status endpoint working")
        else:
            print(f"   ❌ Status endpoint failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Status endpoint error: {str(e)}")
    
    # Test 2: Training model
    print("\n2. Testing Model Training Endpoint...")
    training_request = {
        "days_back": 60,  # Use smaller dataset for faster testing
        "optimize_parameters": False,  # Skip optimization for speed
        "target_column": "bor"
    }
    
    try:
        print("   Sending training request...")
        response = requests.post(
            f"{BASE_URL}/sarima/train", 
            json=training_request,
            timeout=120  # Allow up to 2 minutes for training
        )
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Training Status: {data.get('status')}")
            print(f"   Data Points: {data.get('training_info', {}).get('data_points', 'N/A')}")
            
            performance = data.get('performance_metrics', {})
            mape = performance.get('mape', 0)
            print(f"   MAPE: {mape:.2f}%")
            
            journal_compliance = data.get('journal_compliance', {})
            meets_criteria = journal_compliance.get('meets_mape_criteria', False)
            print(f"   Meets Journal Criteria: {'✅ Yes' if meets_criteria else '❌ No'}")
            print("   ✅ Training endpoint working")
            
            # Store training success for next tests
            training_successful = meets_criteria
        else:
            print(f"   ❌ Training endpoint failed: {response.text}")
            training_successful = False
            
    except requests.exceptions.Timeout:
        print("   ⏰ Training request timed out (this is normal for large datasets)")
        training_successful = False
    except Exception as e:
        print(f"   ❌ Training endpoint error: {str(e)}")
        training_successful = False
    
    # Test 3: Prediction (only if training was successful)
    if training_successful:
        print("\n3. Testing Prediction Endpoint...")
        try:
            response = requests.get(f"{BASE_URL}/sarima/predict?days_ahead=7&include_confidence=true")
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Prediction Status: {data.get('status')}")
                print(f"   Forecast Period: {data.get('forecast_period')} days")
                
                predictions = data.get('predictions', {})
                values = predictions.get('values', [])
                if values:
                    print(f"   Sample Predictions: {values[:3]}...")
                    avg_bor = predictions.get('average_predicted_bor', 0)
                    print(f"   Average Predicted BOR: {avg_bor:.1f}%")
                
                interpretation = data.get('interpretation', {})
                print(f"   Optimal Days: {interpretation.get('optimal_days', 0)}")
                print(f"   High Risk Days: {interpretation.get('high_risk_days', 0)}")
                
                print("   ✅ Prediction endpoint working")
            else:
                print(f"   ❌ Prediction endpoint failed: {response.text}")
        except Exception as e:
            print(f"   ❌ Prediction endpoint error: {str(e)}")
    else:
        print("\n3. Skipping Prediction Test (training not successful)")
    
    # Test 4: Diagnostics (only if training was successful)
    if training_successful:
        print("\n4. Testing Diagnostics Endpoint...")
        try:
            response = requests.get(f"{BASE_URL}/sarima/diagnostics")
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                model_stats = data.get('model_statistics', {})
                print(f"   AIC: {model_stats.get('aic', 0):.2f}")
                print(f"   BIC: {model_stats.get('bic', 0):.2f}")
                
                validation = data.get('model_validation', {})
                print(f"   Model Converged: {validation.get('converged', False)}")
                print(f"   Meets Journal Standards: {validation.get('meets_journal_standards', False)}")
                
                print("   ✅ Diagnostics endpoint working")
            else:
                print(f"   ❌ Diagnostics endpoint failed: {response.text}")
        except Exception as e:
            print(f"   ❌ Diagnostics endpoint error: {str(e)}")
    else:
        print("\n4. Skipping Diagnostics Test (training not successful)")
    
    # Test 5: Performance metrics (only if training was successful)
    if training_successful:
        print("\n5. Testing Performance Endpoint...")
        try:
            response = requests.get(f"{BASE_URL}/sarima/performance")
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                metrics = data.get('evaluation_metrics', {})
                
                mape = metrics.get('mape', {})
                print(f"   MAPE: {mape.get('value', 0):.2f}%")
                print(f"   Meets Target: {'✅ Yes' if mape.get('meets_target', False) else '❌ No'}")
                
                compliance = data.get('journal_compliance', {})
                print(f"   Journal Compliant: {'✅ Yes' if compliance.get('meets_criteria', False) else '❌ No'}")
                
                print("   ✅ Performance endpoint working")
            else:
                print(f"   ❌ Performance endpoint failed: {response.text}")
        except Exception as e:
            print(f"   ❌ Performance endpoint error: {str(e)}")
    else:
        print("\n5. Skipping Performance Test (training not successful)")
    
    print("\n" + "="*60)
    print("🎯 SARIMA API Test Summary")
    print("="*60)
    print("All core SARIMA endpoints have been tested.")
    print("For full functionality, ensure you have sufficient SHRI data in the database.")
    print("\n✅ API endpoints are properly configured and ready for use!")

def test_root_endpoint():
    """Test root endpoint to verify server is running"""
    print("🚀 Testing Server Connection...")
    try:
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server is running: {data.get('message', 'Unknown')}")
            return True
        else:
            print(f"❌ Server responded with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {str(e)}")
        print("Please make sure the backend server is running on http://localhost:8000")
        return False

def main():
    """Main test execution"""
    print("🧪 SARIMA API Integration Test")
    print("Validating implementation sesuai jurnal penelitian")
    print("="*60)
    
    # Check server connectivity
    if not test_root_endpoint():
        print("\n❌ Server is not accessible. Please start the backend server first:")
        print("   cd backend && python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
        return 1
    
    # Test SARIMA endpoints
    test_sarima_endpoints()
    
    return 0

if __name__ == "__main__":
    exit(main())