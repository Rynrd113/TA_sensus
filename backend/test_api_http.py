"""
Quick test untuk endpoint API menggunakan requests library
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1/prediksi"

def test_model_status():
    """Test GET /api/v1/prediksi/status"""
    print("\n" + "="*60)
    print("TEST: GET /api/v1/prediksi/status")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/status", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Status: SUCCESS")
            print(json.dumps(data, indent=2))
        else:
            print(f"❌ Status Code: {response.status_code}")
            print(response.text)
    except requests.exceptions.ConnectionError:
        print("⚠️  Server tidak berjalan. Jalankan: uvicorn main:app --reload")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_prediction_post():
    """Test POST /api/v1/prediksi"""
    print("\n" + "="*60)
    print("TEST: POST /api/v1/prediksi (n_days=7, CI=0.95)")
    print("="*60)
    
    try:
        payload = {
            "n_days": 7,
            "confidence_interval": 0.95
        }
        
        response = requests.post(
            BASE_URL,
            json=payload,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Status: SUCCESS")
            print(f"\nPredictions ({len(data['predictions'])} days):")
            print(f"{'Date':<12} {'Predicted':>10} {'Lower':>10} {'Upper':>10}")
            print("-" * 46)
            
            for pred in data['predictions']:
                print(f"{pred['date']:<12} {pred['predicted_value']:>10.1f}% "
                      f"{pred['lower_bound']:>10.1f}% {pred['upper_bound']:>10.1f}%")
            
            print(f"\nModel Info:")
            model_info = data['model_info']
            print(f"  Type: {model_info['model_type']}")
            print(f"  MAPE: {model_info['mape']}%")
            print(f"  RMSE: {model_info.get('rmse', 'N/A')}")
            print(f"  MAE: {model_info.get('mae', 'N/A')}")
            print(f"  Last Trained: {model_info['last_trained']}")
        else:
            print(f"❌ Status Code: {response.status_code}")
            print(response.text)
    except requests.exceptions.ConnectionError:
        print("⚠️  Server tidak berjalan. Jalankan: uvicorn main:app --reload")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_prediction_get_legacy():
    """Test GET /api/v1/prediksi/bor (legacy)"""
    print("\n" + "="*60)
    print("TEST: GET /api/v1/prediksi/bor?hari=7 (legacy)")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/bor?hari=7", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Status: SUCCESS")
            print(f"\nPredictions ({len(data['prediksi'])} days):")
            
            for pred in data['prediksi']:
                print(f"  {pred['tanggal']}: {pred['bor']}%")
            
            if 'rekomendasi' in data:
                print(f"\nRekomendasi: {data['rekomendasi']}")
        else:
            print(f"❌ Status Code: {response.status_code}")
            print(response.text)
    except requests.exceptions.ConnectionError:
        print("⚠️  Server tidak berjalan. Jalankan: uvicorn main:app --reload")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_multiple_timeframes():
    """Test prediksi untuk berbagai timeframe"""
    print("\n" + "="*60)
    print("TEST: Multiple Timeframes (7, 14, 30 days)")
    print("="*60)
    
    for n_days in [7, 14, 30]:
        print(f"\n📊 Prediksi {n_days} hari:")
        
        try:
            payload = {
                "n_days": n_days,
                "confidence_interval": 0.95
            }
            
            response = requests.post(BASE_URL, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                predictions = [p['predicted_value'] for p in data['predictions']]
                
                print(f"  ✅ Success")
                print(f"     Rata-rata: {sum(predictions)/len(predictions):.1f}%")
                print(f"     Range: {min(predictions):.1f}% - {max(predictions):.1f}%")
            else:
                print(f"  ❌ Failed: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("  ⚠️  Server tidak berjalan")
            break
        except Exception as e:
            print(f"  ❌ Error: {e}")

def main():
    print("\n" + "="*60)
    print("🧪 API INTEGRATION TEST - HTTP REQUESTS")
    print("="*60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Base URL: {BASE_URL}")
    
    # Run tests
    test_model_status()
    test_prediction_post()
    test_prediction_get_legacy()
    test_multiple_timeframes()
    
    print("\n" + "="*60)
    print("✅ TEST SELESAI")
    print("="*60)
    print("\nCatatan:")
    print("  - Jika server tidak berjalan, jalankan: uvicorn main:app --reload")
    print("  - Akses Swagger UI: http://localhost:8000/docs")
    print("  - Akses ReDoc: http://localhost:8000/redoc")

if __name__ == "__main__":
    main()
