# backend/api/v1/export_router.py
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime, date
import pandas as pd
from io import BytesIO
from typing import Optional
import joblib
import os

from backend.database.session import get_db
from backend.models.sensus import SensusHarian
from backend.services.indikator_service import hitung_indikator_bulanan

router = APIRouter(prefix="/export", tags=["export"])

@router.get("/excel")
def export_to_excel(
    bulan: Optional[int] = Query(None, description="Bulan (1-12)"),
    tahun: Optional[int] = Query(None, description="Tahun"),
    format_type: str = Query("lengkap", description="Format: 'lengkap', 'ringkas', atau 'indikator'"),
    db: Session = Depends(get_db)
):
    """Export data sensus ke format Excel"""
    try:
        # Default ke bulan dan tahun sekarang
        if not bulan:
            bulan = datetime.now().month
        if not tahun:
            tahun = datetime.now().year
            
        # Query data sensus
        query = db.query(SensusHarian)
        
        if bulan and tahun:
            query = query.filter(
                SensusHarian.tanggal >= date(tahun, bulan, 1)
            )
            if bulan == 12:
                next_month = date(tahun + 1, 1, 1)
            else:
                next_month = date(tahun, bulan + 1, 1)
            query = query.filter(SensusHarian.tanggal < next_month)
        
        data_sensus = query.order_by(SensusHarian.tanggal).all()
        
        if not data_sensus:
            raise HTTPException(status_code=404, detail="Tidak ada data")
        
        # Buat DataFrame
        df_sensus = pd.DataFrame([
            {
                "Tanggal": d.tanggal.strftime('%d/%m/%Y'),
                "Hari": d.tanggal.strftime('%A'),
                "Pasien Awal": d.jml_pasien_awal,
                "Pasien Masuk": d.jml_masuk,
                "Pasien Keluar": d.jml_keluar,
                "Pasien Akhir": d.jml_pasien_akhir,
                "TT Tersedia": d.tempat_tidur_tersedia,
                "BOR (%)": round(d.bor, 1) if d.bor else 0,
                "Status": "Kritis" if d.bor and d.bor > 85 else "Optimal" if d.bor and d.bor >= 60 else "Rendah"
            } for d in data_sensus
        ])
        
        # Export ke Excel
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df_sensus.to_excel(writer, sheet_name='Data Sensus', index=False)
            
            # Format sheet
            worksheet = writer.sheets['Data Sensus']
            workbook = writer.book
            
            # Header format
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#4472C4',
                'font_color': 'white',
                'border': 1,
                'align': 'center'
            })
            
            # Apply header format
            for col_num, value in enumerate(df_sensus.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            # Auto-adjust column widths
            for i, col in enumerate(df_sensus.columns):
                max_len = max(df_sensus[col].astype(str).map(len).max(), len(col)) + 2
                worksheet.set_column(i, i, max_len)
        
        buffer.seek(0)
        
        # Nama file
        nama_file = f"sensus_rs_{bulan:02d}_{tahun}.xlsx"
        
        return StreamingResponse(
            BytesIO(buffer.read()),
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={"Content-Disposition": f"attachment; filename={nama_file}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/excel-prediksi")
def export_excel_dengan_prediksi(
    bulan: Optional[int] = Query(None, description="Bulan (1-12)"),
    tahun: Optional[int] = Query(None, description="Tahun"),
    hari_prediksi: int = Query(7, description="Jumlah hari prediksi"),
    db: Session = Depends(get_db)
):
    """Export data sensus lengkap dengan prediksi BOR ke Excel"""
    try:
        # Default ke bulan dan tahun sekarang
        if not bulan:
            bulan = datetime.now().month
        if not tahun:
            tahun = datetime.now().year
            
        # Query data sensus
        query = db.query(SensusHarian)
        
        if bulan and tahun:
            query = query.filter(
                SensusHarian.tanggal >= date(tahun, bulan, 1)
            )
            if bulan == 12:
                next_month = date(tahun + 1, 1, 1)
            else:
                next_month = date(tahun, bulan + 1, 1)
            query = query.filter(SensusHarian.tanggal < next_month)
        
        data_sensus = query.order_by(SensusHarian.tanggal).all()
        
        if not data_sensus:
            raise HTTPException(status_code=404, detail="Tidak ada data")
        
        # Buat DataFrame data sensus
        df_sensus = pd.DataFrame([
            {
                "Tanggal": d.tanggal.strftime('%d/%m/%Y'),
                "Hari": d.tanggal.strftime('%A'),
                "Pasien Awal": d.jml_pasien_awal,
                "Pasien Masuk": d.jml_masuk,
                "Pasien Keluar": d.jml_keluar,
                "Pasien Akhir": d.jml_pasien_akhir,
                "TT Tersedia": d.tempat_tidur_tersedia,
                "BOR (%)": round(d.bor, 1) if d.bor else 0,
                "Status": "Kritis" if d.bor and d.bor > 85 else "Optimal" if d.bor and d.bor >= 60 else "Rendah",
                "LOS": round(d.los, 1) if d.los else 0,
                "BTO": round(d.bto, 1) if d.bto else 0,
                "TOI": round(d.toi, 1) if d.toi else 0
            } for d in data_sensus
        ])
        
        # Generate prediksi BOR
        df_prediksi = pd.DataFrame()
        model_path = "backend/ml/model.pkl"
        
        if os.path.exists(model_path):
            try:
                model = joblib.load(model_path)
                forecast = model.forecast(steps=hari_prediksi)
                
                # Generate tanggal prediksi
                last_date = data_sensus[-1].tanggal if data_sensus else date.today()
                dates = pd.date_range(
                    last_date + pd.Timedelta(days=1),
                    periods=hari_prediksi
                ).strftime('%d/%m/%Y').tolist()
                
                df_prediksi = pd.DataFrame([
                    {
                        "Tanggal": dates[i],
                        "Hari": pd.to_datetime(dates[i], format='%d/%m/%Y').strftime('%A'),
                        "BOR Prediksi (%)": round(float(forecast[i]), 1),
                        "Status Prediksi": "Kritis" if forecast[i] > 85 else "Optimal" if forecast[i] >= 60 else "Rendah",
                        "Rekomendasi": (
                            "Siapkan kamar cadangan & tambah tenaga" if forecast[i] > 90 else
                            "Pantau kesiapan tempat tidur" if forecast[i] > 80 else
                            "Kondisi normal"
                        )
                    } for i in range(hari_prediksi)
                ])
            except Exception as e:
                print(f"Error generating prediction: {e}")
        
        # Hitung indikator bulanan
        tt_total = data_sensus[-1].tempat_tidur_tersedia if data_sensus else 0
        indikator_bulanan = hitung_indikator_bulanan(data_sensus, tt_total)
        
        # Export ke Excel dengan multiple sheets
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            workbook = writer.book
            
            # Sheet 1: Data Sensus Harian
            df_sensus.to_excel(writer, sheet_name='Data Sensus', index=False)
            worksheet1 = writer.sheets['Data Sensus']
            
            # Format header
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#4472C4',
                'font_color': 'white',
                'border': 1,
                'align': 'center'
            })
            
            for col_num, value in enumerate(df_sensus.columns.values):
                worksheet1.write(0, col_num, value, header_format)
                max_len = max(
                    df_sensus[value].astype(str).map(len).max() if len(df_sensus) > 0 else 0, 
                    len(str(value))
                ) + 2
                worksheet1.set_column(col_num, col_num, max_len)
            
            # Sheet 2: Prediksi BOR (jika ada)
            if not df_prediksi.empty:
                df_prediksi.to_excel(writer, sheet_name='Prediksi BOR', index=False)
                worksheet2 = writer.sheets['Prediksi BOR']
                
                for col_num, value in enumerate(df_prediksi.columns.values):
                    worksheet2.write(0, col_num, value, header_format)
                    max_len = max(
                        df_prediksi[value].astype(str).map(len).max() if len(df_prediksi) > 0 else 0, 
                        len(str(value))
                    ) + 2
                    worksheet2.set_column(col_num, col_num, max_len)
            
            # Sheet 3: Ringkasan Indikator
            df_ringkasan = pd.DataFrame([
                {"Indikator": "Rata-rata BOR (%)", "Nilai": round(sum(d.bor for d in data_sensus) / len(data_sensus), 1), "Standar": "60-85%"},
                {"Indikator": "LOS - Length of Stay (hari)", "Nilai": indikator_bulanan['los'], "Standar": "6-9 hari"},
                {"Indikator": "BTO - Bed Turn Over", "Nilai": indikator_bulanan['bto'], "Standar": "40-50x/tahun"},
                {"Indikator": "TOI - Turn Over Interval (hari)", "Nilai": indikator_bulanan['toi'], "Standar": "1-3 hari"},
                {"Indikator": "Total Pasien Masuk", "Nilai": sum(d.jml_masuk for d in data_sensus), "Standar": "-"},
                {"Indikator": "Total Pasien Keluar", "Nilai": sum(d.jml_keluar for d in data_sensus), "Standar": "-"},
                {"Indikator": "Total Tempat Tidur", "Nilai": tt_total, "Standar": "-"},
                {"Indikator": "Periode Data", "Nilai": f"{len(data_sensus)} hari", "Standar": "-"}
            ])
            
            df_ringkasan.to_excel(writer, sheet_name='Ringkasan Indikator', index=False)
            worksheet3 = writer.sheets['Ringkasan Indikator']
            
            for col_num, value in enumerate(df_ringkasan.columns.values):
                worksheet3.write(0, col_num, value, header_format)
                max_len = max(
                    df_ringkasan[value].astype(str).map(len).max() if len(df_ringkasan) > 0 else 0, 
                    len(str(value))
                ) + 2
                worksheet3.set_column(col_num, col_num, max_len)
        
        buffer.seek(0)
        
        # Nama file
        nama_file = f"laporan_sensus_prediksi_{bulan:02d}_{tahun}.xlsx"
        
        return StreamingResponse(
            BytesIO(buffer.read()),
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={"Content-Disposition": f"attachment; filename={nama_file}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/csv")
def export_to_csv(
    bulan: Optional[int] = Query(None, description="Bulan (1-12)"),
    tahun: Optional[int] = Query(None, description="Tahun"),
    db: Session = Depends(get_db)
):
    """Export data sensus ke format CSV"""
    try:
        # Default ke bulan dan tahun sekarang
        if not bulan:
            bulan = datetime.now().month
        if not tahun:
            tahun = datetime.now().year
            
        # Query data
        query = db.query(SensusHarian)
        if bulan and tahun:
            query = query.filter(
                SensusHarian.tanggal >= date(tahun, bulan, 1)
            )
            if bulan == 12:
                next_month = date(tahun + 1, 1, 1)
            else:
                next_month = date(tahun, bulan + 1, 1)
            query = query.filter(SensusHarian.tanggal < next_month)
        
        data_sensus = query.order_by(SensusHarian.tanggal).all()
        
        if not data_sensus:
            raise HTTPException(status_code=404, detail="Tidak ada data")
        
        # Buat DataFrame
        df = pd.DataFrame([
            {
                "tanggal": d.tanggal.strftime('%Y-%m-%d'),
                "pasien_awal": d.jml_pasien_awal,
                "masuk": d.jml_masuk,
                "keluar": d.jml_keluar,
                "pasien_akhir": d.jml_pasien_akhir,
                "tt_tersedia": d.tempat_tidur_tersedia,
                "bor_persen": d.bor
            } for d in data_sensus
        ])
        
        # Convert ke CSV
        csv_data = df.to_csv(index=False)
        
        return StreamingResponse(
            BytesIO(csv_data.encode('utf-8')),
            media_type='text/csv',
            headers={"Content-Disposition": f"attachment; filename=sensus_{bulan:02d}_{tahun}.csv"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
