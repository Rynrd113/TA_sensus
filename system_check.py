#!/usr/bin/env python3
# system_check.py - Verifikasi otomatis semua komponen sistem

import os
import sys
import subprocess
import requests
import time
from pathlib import Path

class SystemChecker:
    def __init__(self):
        self.base_path = Path("/home/rynrd/Documents/Project/TA/sensus-rs/sensus-rs")
        self.results = []
        
    def log_result(self, test_name, status, message=""):
        """Log hasil test"""
        icon = "✅" if status else "❌"
        self.results.append((test_name, status, message))
        print(f"{icon} {test_name}: {message}")
    
    def check_file_exists(self, file_path, description):
        """Cek apakah file ada"""
        full_path = self.base_path / file_path
        exists = full_path.exists()
        self.log_result(f"File {description}", exists, str(full_path))
        return exists
    
    def check_backend_structure(self):
        """Cek struktur backend"""
        print("\n🔧 Checking Backend Structure...")
        
        files = [
            ("backend/main.py", "Main FastAPI app"),
            ("backend/models/sensus.py", "Database models"),
            ("backend/schemas/sensus.py", "Pydantic schemas"),
            ("backend/api/v1/sensus_router.py", "Sensus API router"),
            ("backend/api/v1/prediksi_router.py", "Prediksi API router"),
            ("backend/ml/train.py", "ML training script"),
            ("backend/core/logging_config.py", "Logging configuration"),
            ("backend/tests/test_sensus.py", "Unit tests"),
        ]
        
        for file_path, desc in files:
            self.check_file_exists(file_path, desc)
    
    def check_frontend_structure(self):
        """Cek struktur frontend"""
        print("\n🎨 Checking Frontend Structure...")
        
        files = [
            ("frontend/package.json", "Package.json"),
            ("frontend/src/App.tsx", "Main App component"),
            ("frontend/src/components/forms/SensusForm.tsx", "Sensus form"),
            ("frontend/src/components/dashboard/DataGrid.tsx", "Data grid"),
            ("frontend/src/pages/DashboardPage.tsx", "Dashboard page"),
            ("frontend/src/pages/SensusPage.tsx", "Sensus page"),
        ]
        
        for file_path, desc in files:
            self.check_file_exists(file_path, desc)
    
    def check_dependencies(self):
        """Cek dependencies Python"""
        print("\n📦 Checking Python Dependencies...")
        
        required_packages = [
            "fastapi", "uvicorn", "sqlalchemy", "pydantic", 
            "pandas", "statsmodels", "joblib", "pytest"
        ]
        
        for package in required_packages:
            try:
                __import__(package)
                self.log_result(f"Package {package}", True, "Installed")
            except ImportError:
                self.log_result(f"Package {package}", False, "Missing")
    
    def check_database(self):
        """Cek database"""
        print("\n💾 Checking Database...")
        
        # Cek file database
        db_file = self.base_path / "sensus.db"
        if db_file.exists():
            self.log_result("Database file", True, str(db_file))
            
            # Cek koneksi database
            try:
                import sqlite3
                conn = sqlite3.connect(str(db_file))
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM sensus_harian")
                count = cursor.fetchone()[0]
                conn.close()
                self.log_result("Database connection", True, f"{count} records")
            except Exception as e:
                self.log_result("Database connection", False, str(e))
        else:
            self.log_result("Database file", False, "Not found")
    
    def check_ml_model(self):
        """Cek ML model"""
        print("\n🤖 Checking ML Model...")
        
        model_file = self.base_path / "backend/ml/model.pkl"
        if model_file.exists():
            self.log_result("ML Model file", True, str(model_file))
            
            # Test load model
            try:
                import joblib
                model = joblib.load(str(model_file))
                self.log_result("ML Model loading", True, f"Type: {type(model).__name__}")
            except Exception as e:
                self.log_result("ML Model loading", False, str(e))
        else:
            self.log_result("ML Model file", False, "Not found - run train.py first")
    
    def check_api_endpoints(self):
        """Cek API endpoints (jika server running)"""
        print("\n🌐 Checking API Endpoints...")
        
        base_url = "http://localhost:8000"
        endpoints = [
            "/", 
            "/sensus", 
            "/prediksi/bor", 
            "/dashboard/stats",
            "/docs"
        ]
        
        try:
            # Test root endpoint
            response = requests.get(f"{base_url}/", timeout=5)
            if response.status_code == 200:
                self.log_result("API Server", True, "Running on localhost:8000")
                
                for endpoint in endpoints[1:]:
                    try:
                        resp = requests.get(f"{base_url}{endpoint}", timeout=3)
                        self.log_result(f"Endpoint {endpoint}", resp.status_code < 500, f"Status: {resp.status_code}")
                    except Exception as e:
                        self.log_result(f"Endpoint {endpoint}", False, str(e))
            else:
                self.log_result("API Server", False, f"Status: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            self.log_result("API Server", False, "Not running - start with 'uvicorn backend.main:app --reload'")
        except Exception as e:
            self.log_result("API Server", False, str(e))
    
    def generate_report(self):
        """Generate summary report"""
        print("\n" + "="*50)
        print("📊 SYSTEM CHECK SUMMARY")
        print("="*50)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for _, status, _ in self.results if status)
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for test_name, status, message in self.results:
                if not status:
                    print(f"  - {test_name}: {message}")
        
        print("\n" + "="*50)
        
        if passed_tests >= total_tests * 0.8:  # 80% pass rate
            print("🎉 SISTEM READY!")
            print("Sistem sudah siap untuk digunakan dan dipresentasikan.")
        else:
            print("⚠️  PERLU PERBAIKAN")
            print("Ada beberapa komponen yang perlu diperbaiki.")
        
        return passed_tests >= total_tests * 0.8

def main():
    print("🚀 SYSTEM CHECK - SENSUS-RS")
    print("Memeriksa semua komponen sistem...")
    
    checker = SystemChecker()
    
    # Run all checks
    checker.check_backend_structure()
    checker.check_frontend_structure()
    checker.check_dependencies()
    checker.check_database()
    checker.check_ml_model()
    checker.check_api_endpoints()
    
    # Generate report
    success = checker.generate_report()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
