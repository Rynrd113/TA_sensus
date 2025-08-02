#!/usr/bin/env python3
import sys
import os
sys.path.append('/home/rynrd/Documents/Project/TA/sensus-rs/sensus-rs')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models.sensus import SensusHarian

# Database connection
DATABASE_URL = "sqlite:///./db/sensus.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_db():
    db = SessionLocal()
    try:
        # Test query
        data = db.query(SensusHarian).all()
        print(f"Total records: {len(data)}")
        
        if data:
            print("\nFirst few records:")
            for item in data[:3]:
                print(f"Date: {item.tanggal}, BOR: {item.bor}, Pasien: {item.jml_pasien_akhir}")
        
        # Test specific month
        from sqlalchemy import extract
        july_data = db.query(SensusHarian).filter(
            extract('month', SensusHarian.tanggal) == 7,
            extract('year', SensusHarian.tanggal) == 2025
        ).all()
        
        print(f"\nJuly 2025 records: {len(july_data)}")
        for item in july_data:
            print(f"Date: {item.tanggal}, BOR: {item.bor}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_db()
