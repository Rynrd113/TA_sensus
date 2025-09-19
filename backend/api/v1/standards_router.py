# backend/api/v1/standards_router.py
"""
Router untuk medical standards endpoint
"""
from fastapi import APIRouter
from utils.indikator_calculator import IndikatorCalculator

router = APIRouter(prefix="/standards", tags=["medical-standards"])

@router.get("/medical")
def get_medical_standards():
    """
    Ambil semua medical standards untuk frontend
    Endpoint ini memungkinkan frontend menggunakan threshold yang sama
    """
    standards = IndikatorCalculator.get_medical_standards()
    return {
        "status": "success",
        "data": standards,
        "message": "Medical standards retrieved successfully"
    }

@router.get("/medical/bor")
def get_bor_standards():
    """Get BOR specific standards"""
    standards = IndikatorCalculator.get_medical_standards()
    return {
        "status": "success", 
        "data": standards["BOR"],
        "message": "BOR standards retrieved successfully"
    }

@router.get("/medical/los")
def get_los_standards():
    """Get LOS specific standards"""
    standards = IndikatorCalculator.get_medical_standards()
    return {
        "status": "success",
        "data": standards["LOS"], 
        "message": "LOS standards retrieved successfully"
    }

@router.get("/medical/bto")
def get_bto_standards():
    """Get BTO specific standards"""
    standards = IndikatorCalculator.get_medical_standards()
    return {
        "status": "success",
        "data": standards["BTO"],
        "message": "BTO standards retrieved successfully"
    }