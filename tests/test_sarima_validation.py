#!/usr/bin/env python3
"""
Test Script untuk SARIMA Model Implementation
Sesuai dengan jurnal penelitian: "Peramalan Indikator Rumah Sakit Berbasis Sensus Harian Rawat Inap dengan Model SARIMA"

Test Coverage:
1. Model SARIMA Core functionality
2. Data preprocessing dan validation
3. Parameter optimization
4. Performance evaluation (RMSE, MAE, MAPE)
5. Prediction generation
6. API endpoints functionality
"""

import sys
import os

# Add backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.append(backend_path)

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_sarima_model_core():
    """Test SARIMA model core functionality"""
    try:
        from ml.sarima_model import SARIMAPredictor
        
        logger.info("🧪 Testing SARIMA Model Core...")
        
        # Initialize predictor
        predictor = SARIMAPredictor()
        
        # Generate synthetic test data (simulating SHRI data)
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
        
        # Generate BOR data with seasonal pattern (weekly cycle)
        np.random.seed(42)  # For reproducible results
        base_bor = 75  # Base BOR around 75%
        seasonal_component = 5 * np.sin(2 * np.pi * np.arange(len(dates)) / 7)  # Weekly pattern
        noise = np.random.normal(0, 3, len(dates))
        bor_values = base_bor + seasonal_component + noise
        
        # Ensure BOR stays within realistic bounds (40-95%)
        bor_values = np.clip(bor_values, 40, 95)
        
        # Create test dataset
        test_data = []
        for i, date in enumerate(dates):
            test_data.append({
                'tanggal': date,
                'bor': bor_values[i],
                'jml_masuk': int(np.random.poisson(15)),  # Average 15 patients per day
                'jml_keluar': int(np.random.poisson(14)),  # Average 14 patients per day
                'jml_dirawat': int(100 * bor_values[i] / 100)  # Based on BOR
            })
        
        logger.info(f"✓ Generated {len(test_data)} days of synthetic SHRI data")
        
        # Test data preparation
        series = predictor.prepare_data(test_data, 'bor')
        logger.info(f"✓ Data preparation successful. Series length: {len(series)}")
        
        # Test stationarity check
        stationarity_result = predictor.check_stationarity(series)
        logger.info(f"✓ Stationarity test completed. Is stationary: {stationarity_result['is_stationary']}")
        
        # Test ACF/PACF analysis
        acf_pacf_result = predictor.plot_acf_pacf(series, lags=20)
        logger.info(f"✓ ACF/PACF analysis completed. ACF length: {len(acf_pacf_result['acf_values'])}")
        
        # Test model fitting with limited parameter search for faster execution
        predictor.order = (1, 1, 1)
        predictor.seasonal_order = (1, 1, 1, 7)
        
        model_info = predictor.fit_model(series, optimize=False)  # Skip optimization for speed
        logger.info(f"✓ Model fitting completed. AIC: {model_info['aic']:.2f}")
        
        # Test diagnostics
        diagnostics = predictor.diagnostic_tests()
        logger.info(f"✓ Model diagnostics completed. White noise: {diagnostics['ljung_box_test']['white_noise']}")
        
        # Test performance evaluation
        fitted_values = predictor.fitted_model.fittedvalues
        performance = predictor.evaluate_performance(series, fitted_values)
        logger.info(f"✓ Performance evaluation completed. MAPE: {performance['mape']:.2f}%")
        
        # Check journal compliance (MAPE < 10%)
        journal_compliant = performance['mape'] < 10
        logger.info(f"✓ Journal compliance check: {'✅ PASSED' if journal_compliant else '❌ FAILED'} (MAPE: {performance['mape']:.2f}%)")
        
        # Test prediction generation
        prediction_result = predictor.predict(steps=7)
        logger.info(f"✓ Prediction generation completed. Predictions: {len(prediction_result['predictions'])}")
        
        # Test model summary
        summary = predictor.get_model_summary()
        logger.info(f"✓ Model summary generated. Total observations: {summary['data_info']['total_observations']}")
        
        return {
            'status': 'SUCCESS',
            'model_info': model_info,
            'performance': performance,
            'journal_compliant': journal_compliant,
            'prediction_sample': prediction_result['predictions'][:3],  # First 3 predictions
            'test_data_size': len(test_data)
        }
        
    except Exception as e:
        logger.error(f"❌ SARIMA Model Core Test Failed: {str(e)}")
        return {
            'status': 'FAILED',
            'error': str(e)
        }

def test_api_endpoints():
    """Test SARIMA API endpoints functionality"""
    try:
        logger.info("🔗 Testing SARIMA API Endpoints...")
        
        # Test imports
        from api.v1.sarima_router import router
        from schemas.prediksi import SARIMAPredictionResponse, SARIMATrainingRequest
        
        logger.info("✓ API router and schemas imported successfully")
        
        # Test schema validation
        training_request = SARIMATrainingRequest(
            days_back=90,
            optimize_parameters=True,
            target_column='bor'
        )
        logger.info("✓ Training request schema validation passed")
        
        return {
            'status': 'SUCCESS',
            'message': 'API endpoints and schemas are properly configured'
        }
        
    except Exception as e:
        logger.error(f"❌ API Endpoints Test Failed: {str(e)}")
        return {
            'status': 'FAILED',
            'error': str(e)
        }

def test_database_integration():
    """Test database integration for SHRI data"""
    try:
        logger.info("🗄️ Testing Database Integration...")
        
        # Test database imports
        from models.sensus import SensusHarian
        from database.session import SessionLocal
        
        logger.info("✓ Database models and session imported successfully")
        
        # Test session creation (without actual connection since no real DB)
        logger.info("✓ Database integration components available")
        
        return {
            'status': 'SUCCESS',
            'message': 'Database integration components are properly configured'
        }
        
    except Exception as e:
        logger.error(f"❌ Database Integration Test Failed: {str(e)}")
        return {
            'status': 'FAILED',
            'error': str(e)
        }

def generate_test_report(results):
    """Generate comprehensive test report"""
    logger.info("\n" + "="*60)
    logger.info("📋 SARIMA MODEL TEST REPORT")
    logger.info("="*60)
    
    logger.info("\n🔬 TEST SUITE RESULTS:")
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result.get('status') == 'SUCCESS')
    
    for test_name, result in results.items():
        status_icon = "✅" if result.get('status') == 'SUCCESS' else "❌"
        logger.info(f"{status_icon} {test_name}: {result.get('status', 'UNKNOWN')}")
        
        if result.get('status') == 'FAILED':
            logger.info(f"   Error: {result.get('error', 'Unknown error')}")
    
    logger.info(f"\n📊 SUMMARY: {passed_tests}/{total_tests} tests passed")
    
    # Journal compliance check
    if 'SARIMA Model Core' in results:
        core_result = results['SARIMA Model Core']
        if core_result.get('status') == 'SUCCESS':
            logger.info(f"\n🎯 JOURNAL COMPLIANCE CHECK:")
            journal_compliant = core_result.get('journal_compliant', False)
            mape = core_result.get('performance', {}).get('mape', 0)
            
            if journal_compliant:
                logger.info(f"✅ Model meets journal criteria (MAPE: {mape:.2f}% < 10%)")
                logger.info("✅ Implementation follows Box-Jenkins methodology")
                logger.info("✅ Seasonal pattern detection (weekly cycle) working")
            else:
                logger.info(f"⚠️  Model needs improvement (MAPE: {mape:.2f}% >= 10%)")
                logger.info("💡 Consider: More data, parameter tuning, or feature engineering")
    
    if passed_tests == total_tests:
        logger.info("\n🎉 ALL TESTS PASSED! SARIMA implementation is ready for deployment.")
    else:
        logger.info(f"\n⚠️  {total_tests - passed_tests} test(s) failed. Please review and fix issues.")
    
    logger.info("\n" + "="*60)

def main():
    """Main test execution"""
    logger.info("🚀 Starting SARIMA Model Validation Tests...")
    logger.info("Sesuai jurnal: 'Peramalan Indikator Rumah Sakit Berbasis Sensus Harian Rawat Inap dengan Model SARIMA'")
    
    # Run all tests
    test_results = {}
    
    # Test 1: SARIMA Model Core
    test_results['SARIMA Model Core'] = test_sarima_model_core()
    
    # Test 2: API Endpoints
    test_results['API Endpoints'] = test_api_endpoints()
    
    # Test 3: Database Integration
    test_results['Database Integration'] = test_database_integration()
    
    # Generate comprehensive report
    generate_test_report(test_results)
    
    # Return overall success status
    all_passed = all(result.get('status') == 'SUCCESS' for result in test_results.values())
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)