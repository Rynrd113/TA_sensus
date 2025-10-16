"""Restore CSV from database"""
import sys
sys.path.insert(0, 'backend')

from database.session import SessionLocal
from models.sensus import SensusHarian
import pandas as pd

def restore_csv():
    db = SessionLocal()
    try:
        count = db.query(SensusHarian).count()
        print(f'Database records: {count}')
        
        if count == 0:
            print('No data in database!')
            return
        
        records = db.query(SensusHarian).order_by(SensusHarian.tanggal).all()
        
        data = []
        for r in records:
            data.append({
                'tanggal': r.tanggal,
                'pasien_awal': r.jml_pasien_awal,
                'masuk': r.jml_masuk,
                'keluar': r.jml_keluar,
                'pasien_akhir': r.jml_pasien_akhir,
                'tempat_tidur': r.tempat_tidur_tersedia,
                'hari_rawat': r.hari_rawat,
                'bor': r.bor
            })
        
        df = pd.DataFrame(data)
        print(f'Date range: {df["tanggal"].min()} to {df["tanggal"].max()}')
        print(f'BOR mean: {df["bor"].mean():.2f}%')
        
        df.to_csv('data/shri_training_data.csv', index=False)
        print('✅ CSV restored!')
        
    finally:
        db.close()

if __name__ == "__main__":
    restore_csv()
