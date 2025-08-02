# backend/schemas/sensus.py
from pydantic import BaseModel, Field, field_validator
from datetime import date, datetime
from typing import Optional

class SensusCreate(BaseModel):
    """Schema untuk input data sensus baru dengan validasi ketat"""
    tanggal: str = Field(..., description="Format: YYYY-MM-DD")
    jml_pasien_awal: int = Field(..., ge=0, le=1000, description="Jumlah pasien awal hari")
    jml_masuk: int = Field(..., ge=0, le=500, description="Jumlah pasien masuk")
    jml_keluar: int = Field(..., ge=0, le=500, description="Jumlah pasien keluar")
    tempat_tidur_tersedia: int = Field(..., gt=0, le=1000, description="Jumlah tempat tidur tersedia")
    hari_rawat: Optional[int] = Field(None, ge=0, le=100000, description="Total hari rawat (untuk hitung LOS)")

    @field_validator('jml_pasien_awal', 'jml_masuk', 'jml_keluar', 'tempat_tidur_tersedia')
    @classmethod
    def non_negative_and_realistic(cls, v):
        if v < 0:
            raise ValueError('Nilai tidak boleh negatif')
        if v > 1000:
            raise ValueError('Nilai terlalu besar, maksimal 1000')
        return v
    
    @field_validator('tanggal')
    @classmethod
    def valid_date_format(cls, v):
        try:
            parsed_date = datetime.strptime(v, '%Y-%m-%d').date()
            # Validasi tanggal tidak boleh lebih dari 30 hari ke depan
            from datetime import date, timedelta
            max_date = date.today() + timedelta(days=30)
            if parsed_date > max_date:
                raise ValueError('Tanggal tidak boleh lebih dari 30 hari ke depan')
            # Validasi tanggal tidak boleh lebih dari 1 tahun yang lalu
            min_date = date.today() - timedelta(days=365)
            if parsed_date < min_date:
                raise ValueError('Tanggal tidak boleh lebih dari 1 tahun yang lalu')
        except ValueError as e:
            if "does not match format" in str(e):
                raise ValueError('Format tanggal harus YYYY-MM-DD')
            raise e
        return v
    
    @field_validator('jml_keluar')
    @classmethod
    def keluar_not_exceed_total(cls, v, info):
        if 'jml_pasien_awal' in info.data and 'jml_masuk' in info.data:
            total_available = info.data['jml_pasien_awal'] + info.data['jml_masuk']
            if v > total_available:
                raise ValueError('Pasien keluar tidak boleh melebihi pasien awal + masuk')
        return v
    
    @field_validator('tempat_tidur_tersedia')
    @classmethod
    def validate_tempat_tidur(cls, v, info):
        if 'jml_pasien_awal' in info.data:
            if v < info.data['jml_pasien_awal']:
                raise ValueError('Tempat tidur tidak boleh kurang dari pasien awal')
        return v

class SensusResponse(BaseModel):
    """Schema untuk response data sensus"""
    id: int
    tanggal: date
    jml_pasien_awal: int
    jml_masuk: int
    jml_keluar: int
    jml_pasien_akhir: int
    tempat_tidur_tersedia: int
    bor: float
    los: Optional[float] = None
    bto: Optional[float] = None
    toi: Optional[float] = None
    
    class Config:
        from_attributes = True

class SensusStats(BaseModel):
    """Schema untuk statistik ringkasan"""
    total_records: int
    avg_bor: float
    avg_los: float
    latest_bor: float
    trend: str