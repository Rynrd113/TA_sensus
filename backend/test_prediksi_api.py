"""
Test script untuk endpoint /api/v1/prediksi
Verifikasi integrasi SARIMA model dengan API
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
from datetime import datetime

# Test import
try:
    from api.v1.prediksi_router import (
        load_model_with_cache, 
        PrediksiRequest,
        _MODEL_CACHE
    )
    print("✅ Import modules berhasil")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_model_loading():
    """Test 1: Load model dengan caching"""
    print("\n" + "="*60)
    print("TEST 1: Model Loading dengan Cache")
    print("="*60)
    
    try:
        model, model_info = load_model_with_cache()
        print("✅ Model berhasil di-load")
        print(f"   Model type: {model_info['model_type']}")
        print(f"   MAPE: {model_info['mape']}%")
        print(f"   RMSE: {model_info.get('rmse', 'N/A')}")
        print(f"   MAE: {model_info.get('mae', 'N/A')}")
        print(f"   Last trained: {model_info['last_trained']}")
        
        # Test cache
        model2, model_info2 = load_model_with_cache()
        if model is model2:
            print("✅ Model caching berfungsi dengan baik")
        else:
            print("⚠️  Warning: Model tidak ter-cache")
            
        return True
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return False

def test_prediction_without_confidence():
    """Test 2: Prediksi tanpa confidence interval (legacy)"""
    print("\n" + "="*60)
    print("TEST 2: Prediksi Sederhana (7 hari)")
    print("="*60)
    
    try:
        model, _ = load_model_with_cache()
        
        # Simple forecast
        forecast = model.forecast(steps=7)
        
        print("✅ Prediksi berhasil:")
        for i, value in enumerate(forecast, 1):
            print(f"   Hari {i}: {round(float(value), 1)}%")
            
        return True
    except Exception as e:
        print(f"❌ Error prediksi: {e}")
        return False

def test_prediction_with_confidence():
    """Test 3: Prediksi dengan confidence interval"""
    print("\n" + "="*60)
    print("TEST 3: Prediksi dengan Confidence Interval (95%)")
    print("="*60)
    
    try:
        model, _ = load_model_with_cache()
        
        # Forecast dengan confidence interval
        forecast_result = model.get_forecast(steps=7)
        predicted_mean = forecast_result.predicted_mean
        conf_int = forecast_result.conf_int(alpha=0.05)  # 95% CI
        
        print("✅ Prediksi dengan CI berhasil:")
        print(f"   {'Hari':<6} {'Prediksi':>10} {'Lower':>10} {'Upper':>10}")
        print("   " + "-"*40)
        
        for i in range(7):
            pred = round(float(predicted_mean.iloc[i]), 1)
            lower = round(float(conf_int.iloc[i, 0]), 1)
            upper = round(float(conf_int.iloc[i, 1]), 1)
            print(f"   Hari {i+1:<2} {pred:>10}% {lower:>10}% {upper:>10}%")
            
        return True
    except Exception as e:
        print(f"❌ Error prediksi dengan CI: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_request_schema():
    """Test 4: Validasi request schema"""
    print("\n" + "="*60)
    print("TEST 4: Request Schema Validation")
    print("="*60)
    
    try:
        # Test valid request
        req1 = PrediksiRequest(n_days=7, confidence_interval=0.95)
        print(f"✅ Valid request: n_days={req1.n_days}, CI={req1.confidence_interval}")
        
        # Test default values
        req2 = PrediksiRequest()
        print(f"✅ Default request: n_days={req2.n_days}, CI={req2.confidence_interval}")
        
        # Test boundary values
        req3 = PrediksiRequest(n_days=30, confidence_interval=0.80)
        print(f"✅ Boundary request: n_days={req3.n_days}, CI={req3.confidence_interval}")
        
        # Test invalid values (should raise validation error)
        try:
            req_invalid = PrediksiRequest(n_days=50, confidence_interval=0.5)
            print("❌ Validation seharusnya gagal untuk n_days=50")
        except Exception as e:
            print(f"✅ Validation error tertangkap: {type(e).__name__}")
            
        return True
    except Exception as e:
        print(f"❌ Error schema validation: {e}")
        return False

def test_multiple_predictions():
    """Test 5: Multiple predictions dengan berbagai parameter"""
    print("\n" + "="*60)
    print("TEST 5: Multiple Predictions (7, 14, 30 hari)")
    print("="*60)
    
    try:
        model, _ = load_model_with_cache()
        
        for n_days in [7, 14, 30]:
            forecast_result = model.get_forecast(steps=n_days)
            predicted_mean = forecast_result.predicted_mean
            
            avg_bor = predicted_mean.mean()
            max_bor = predicted_mean.max()
            min_bor = predicted_mean.min()
            
            print(f"\n   Prediksi {n_days} hari:")
            print(f"      Rata-rata: {avg_bor:.1f}%")
            print(f"      Maksimum:  {max_bor:.1f}%")
            print(f"      Minimum:   {min_bor:.1f}%")
        
        print("\n✅ Multiple predictions berhasil")
        return True
    except Exception as e:
        print(f"❌ Error multiple predictions: {e}")
        return False

def test_model_info_complete():
    """Test 6: Kelengkapan informasi model"""
    print("\n" + "="*60)
    print("TEST 6: Kelengkapan Model Info")
    print("="*60)
    
    try:
        _, model_info = load_model_with_cache()
        
        required_fields = ["model_type", "mape", "last_trained"]
        optional_fields = ["rmse", "mae", "aic", "bic"]
        
        print("   Required fields:")
        for field in required_fields:
            if field in model_info:
                print(f"      ✅ {field}: {model_info[field]}")
            else:
                print(f"      ❌ {field}: MISSING")
                return False
        
        print("\n   Optional fields:")
        for field in optional_fields:
            if field in model_info:
                print(f"      ✅ {field}: {model_info[field]}")
            else:
                print(f"      ⚠️  {field}: Not available")
        
        print("\n✅ Model info lengkap")
        return True
    except Exception as e:
        print(f"❌ Error checking model info: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 TEST SUITE: INTEGRASI MODEL SARIMA KE API")
    print("="*60)
    print(f"Waktu test: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Model Loading & Caching", test_model_loading),
        ("Simple Prediction", test_prediction_without_confidence),
        ("Prediction with Confidence Interval", test_prediction_with_confidence),
        ("API Request Schema", test_api_request_schema),
        ("Multiple Predictions", test_multiple_predictions),
        ("Model Info Completeness", test_model_info_complete),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("\n" + "="*60)
    print(f"HASIL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("="*60)
    
    if passed == total:
        print("\n🎉 SEMUA TEST BERHASIL!")
        print("✅ API /api/v1/prediksi siap digunakan")
        print("\nEndpoint tersedia:")
        print("   POST   /api/v1/prediksi        - Prediksi dengan confidence interval")
        print("   GET    /api/v1/prediksi/bor    - Prediksi sederhana (legacy)")
        print("   GET    /api/v1/prediksi/status - Cek status model")
        print("   POST   /api/v1/prediksi/retrain - Retrain model")
        return 0
    else:
        print("\n⚠️  BEBERAPA TEST GAGAL")
        print("Periksa error di atas dan perbaiki sebelum deploy")
        return 1

if __name__ == "__main__":
    exit(main())
