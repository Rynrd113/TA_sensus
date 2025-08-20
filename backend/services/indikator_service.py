# backend/services/indikator_service.py
from datetime import date, timedelta
from typing import List, Dict
from sqlalchemy.orm import Session
from models.sensus import SensusHarian
from utils.indikator_calculator import indikator_calculator

# Re-export untuk backward compatibility
def hitung_indikator_bulanan(
    data_bulanan: List[SensusHarian], 
    tt_total: int,
    periode_hari: int = 30
) -> Dict[str, float]:
    """
    Wrapper function untuk backward compatibility
    Delegates to centralized calculator
    """
    return indikator_calculator.hitung_indikator_bulanan(
        data_bulanan, tt_total, periode_hari
    )

def get_trend_bor(data: List[SensusHarian]) -> str:
    """Wrapper function untuk backward compatibility"""
    return indikator_calculator.get_trend_bor(data)

def generate_peringatan(latest_data: SensusHarian, avg_bor: float) -> List[str]:
    """Wrapper function untuk backward compatibility"""
    return indikator_calculator.generate_peringatan(latest_data, avg_bor)
