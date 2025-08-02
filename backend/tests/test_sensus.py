# backend/tests/test_sensus.py
import pytest
from fastapi.testclient import TestClient
from datetime import date, timedelta
from backend.main import app

client = TestClient(app)

class TestSensusAPI:
    """Test untuk endpoint sensus dengan berbagai skenario"""
    
    def test_create_sensus_valid_data(self):
        """Test input data valid"""
        today = date.today().strftime("%Y-%m-%d")
        data = {
            "tanggal": today,
            "jml_pasien_awal": 40,
            "jml_masuk": 10,
            "jml_keluar": 8,
            "tempat_tidur_tersedia": 50,
            "hari_rawat": 120
        }
        
        response = client.post("/sensus", json=data)
        assert response.status_code in [200, 201, 400]  # 400 jika data sudah ada
        
        if response.status_code in [200, 201]:
            result = response.json()
            assert "bor" in result
            assert result["bor"] >= 0
            assert result["bor"] <= 100
    
    def test_create_sensus_negative_values(self):
        """Test input dengan nilai negatif (harus error)"""
        today = date.today().strftime("%Y-%m-%d")
        data = {
            "tanggal": today,
            "jml_pasien_awal": -5,  # Negatif
            "jml_masuk": 10,
            "jml_keluar": 8,
            "tempat_tidur_tersedia": 50
        }
        
        response = client.post("/sensus", json=data)
        assert response.status_code == 422
        assert "negatif" in response.json()["detail"].lower()
    
    def test_create_sensus_invalid_date_format(self):
        """Test format tanggal salah"""
        data = {
            "tanggal": "2024-13-45",  # Tanggal invalid
            "jml_pasien_awal": 40,
            "jml_masuk": 10,
            "jml_keluar": 8,
            "tempat_tidur_tersedia": 50
        }
        
        response = client.post("/sensus", json=data)
        assert response.status_code == 422
    
    def test_create_sensus_keluar_exceed_total(self):
        """Test pasien keluar melebihi total (harus error)"""
        today = date.today().strftime("%Y-%m-%d")
        data = {
            "tanggal": today,
            "jml_pasien_awal": 10,
            "jml_masuk": 5,
            "jml_keluar": 20,  # Melebihi total (10+5=15)
            "tempat_tidur_tersedia": 50
        }
        
        response = client.post("/sensus", json=data)
        assert response.status_code == 422
        assert "melebihi" in response.json()["detail"].lower()
    
    def test_get_sensus_list(self):
        """Test ambil daftar data sensus"""
        response = client.get("/sensus")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        # Jika ada data, cek struktur
        if len(data) > 0:
            item = data[0]
            required_fields = ["id", "tanggal", "jml_pasien_awal", "bor"]
            for field in required_fields:
                assert field in item
    
    def test_bor_calculation(self):
        """Test kalkulasi BOR benar"""
        # Test data dengan BOR yang bisa dihitung manual
        tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        data = {
            "tanggal": tomorrow,
            "jml_pasien_awal": 30,
            "jml_masuk": 10,
            "jml_keluar": 0,  # Tidak ada yang keluar
            "tempat_tidur_tersedia": 50
        }
        
        response = client.post("/sensus", json=data)
        
        if response.status_code in [200, 201]:
            result = response.json()
            # Pasien akhir = 30 + 10 - 0 = 40
            # BOR = (40 / 50) * 100 = 80%
            expected_bor = 80.0
            assert abs(result["bor"] - expected_bor) < 0.1
    
    def test_stats_summary(self):
        """Test endpoint statistik ringkasan"""
        response = client.get("/sensus/stats/summary")
        assert response.status_code == 200
        
        stats = response.json()
        required_fields = ["total_records", "avg_bor", "latest_bor", "trend"]
        for field in required_fields:
            assert field in stats

class TestPrediksiAPI:
    """Test untuk endpoint prediksi"""
    
    def test_predict_bor_default(self):
        """Test prediksi BOR dengan parameter default"""
        response = client.get("/prediksi/bor")
        assert response.status_code == 200
        
        result = response.json()
        assert "prediksi" in result
        assert "status" in result
        
        if result["status"] == "success":
            assert len(result["prediksi"]) == 3  # Default 3 hari
            for pred in result["prediksi"]:
                assert "tanggal" in pred
                assert "bor" in pred
                assert 0 <= pred["bor"] <= 200  # BOR wajar
    
    def test_predict_bor_custom_days(self):
        """Test prediksi dengan jumlah hari custom"""
        response = client.get("/prediksi/bor?hari=7")
        assert response.status_code == 200
        
        result = response.json()
        if result["status"] == "success":
            assert len(result["prediksi"]) == 7
    
    def test_predict_bor_invalid_days(self):
        """Test prediksi dengan parameter hari invalid"""
        response = client.get("/prediksi/bor?hari=50")  # Terlalu besar
        assert response.status_code == 200
        
        result = response.json()
        assert result["status"] == "error"
        assert "1-30" in result["error"]

class TestDashboardAPI:
    """Test untuk endpoint dashboard"""
    
    def test_dashboard_stats(self):
        """Test dashboard statistik"""
        response = client.get("/dashboard/stats")
        assert response.status_code == 200
        
        stats = response.json()
        # Cek ada data basic
        assert isinstance(stats, dict)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
