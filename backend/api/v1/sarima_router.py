"""
SARIMA API Router for Hospital BOR Prediction
Sesuai dengan penelitian: "Peramalan Indikator Rumah Sakit Berbasis Sensus Harian Rawat Inap dengan Model SARIMA"

Endpoints:
- POST /sarima/train: Training model dengan data SHRI
- GET /sarima/predict: Prediksi BOR periode mendatang  
- GET /sarima/diagnostics: Diagnostik model dan residual analysis
- GET /sarima/performance: Evaluasi performa model (RMSE, MAE, MAPE)
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

# Internal imports
from database.session import get_db
from models.sensus import SensusHarian
from ml.sarima_model import sarima_predictor
from schemas.prediksi import SARIMAPredictionResponse, SARIMATrainingRequest
from core.auth import get_current_user
from models.user import User

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/sarima", tags=["SARIMA Prediction"])

@router.post("/train", response_model=Dict[str, Any])
async def train_sarima_model(
    training_request: SARIMATrainingRequest = Body(...),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Training model SARIMA sesuai metodologi Box-Jenkins
    
    Proses:
    1. Ambil data SHRI dari database
    2. Preprocessing dan transformasi data
    3. Uji stasioneritas (ADF test)
    4. Optimasi parameter (p,d,q)(P,D,Q)s
    5. Fit model dengan MLE
    6. Evaluasi performa (RMSE, MAE, MAPE)
    """
    try:
        logger.info(f"Starting SARIMA training for public access")
        
        # Validate training parameters
        days_back = training_request.days_back or 90
        optimize_params = training_request.optimize_parameters or True
        target_column = training_request.target_column or 'bor'
        
        if days_back < 30:
            raise HTTPException(
                status_code=400, 
                detail="Minimum 30 hari data diperlukan untuk training yang efektif"
            )
        
        # Ambil data SHRI dari database
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        query = db.query(SensusHarian).filter(
            SensusHarian.tanggal >= start_date.date(),
            SensusHarian.tanggal <= end_date.date()
        ).order_by(SensusHarian.tanggal)
        
        data_records = query.all()
        
        if len(data_records) < 30:
            raise HTTPException(
                status_code=400,
                detail=f"Data tidak mencukupi: {len(data_records)} records. Minimum 30 records diperlukan."
            )
        
        # Convert to format untuk SARIMA
        data_list = []
        for record in data_records:
            data_list.append({
                'tanggal': record.tanggal,
                'bor': float(record.bor) if record.bor else 0.0,
                'pasien_masuk': record.jml_masuk or 0,
                'pasien_keluar': record.jml_keluar or 0,
                'pasien_dirawat': record.jml_dirawat or 0
            })
        
        logger.info(f"Retrieved {len(data_list)} records for training")
        
        # Prepare data untuk time series
        series = sarima_predictor.prepare_data(data_list, target_column)
        
        # Check stationarity
        stationarity_test = sarima_predictor.check_stationarity(series)
        
        # Fit model
        model_info = sarima_predictor.fit_model(series, optimize=optimize_params)
        
        # Diagnostic tests
        diagnostics = sarima_predictor.diagnostic_tests()
        
        # Evaluate performance on training data
        fitted_values = sarima_predictor.fitted_model.fittedvalues
        performance = sarima_predictor.evaluate_performance(series, fitted_values)
        
        # Prepare response
        response = {
            "status": "success",
            "message": "Model SARIMA berhasil di-training",
            "training_info": {
                "data_points": len(data_list),
                "date_range": {
                    "start": data_list[0]['tanggal'].strftime('%Y-%m-%d'),
                    "end": data_list[-1]['tanggal'].strftime('%Y-%m-%d')
                },
                "target_column": target_column,
                "optimization_enabled": optimize_params
            },
            "model_info": model_info,
            "stationarity_test": stationarity_test,
            "performance_metrics": performance,
            "diagnostics_summary": {
                "white_noise_residuals": diagnostics['ljung_box_test']['white_noise'],
                "residual_mean": diagnostics['residual_statistics']['mean'],
                "residual_std": diagnostics['residual_statistics']['std']
            },
            "journal_compliance": {
                "methodology": "Box-Jenkins SARIMA",
                "meets_mape_criteria": performance.get('mape', 100) < 10,
                "target_mape": "< 10% (sesuai jurnal)",
                "actual_mape": f"{performance.get('mape', 0):.2f}%"
            }
        }
        
        logger.info(f"SARIMA training completed. MAPE: {performance.get('mape', 0):.2f}%")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in SARIMA training: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error training SARIMA model: {str(e)}"
        )

@router.get("/predict", response_model=SARIMAPredictionResponse)
async def predict_bor(
    days_ahead: int = Query(7, ge=1, le=30, description="Jumlah hari prediksi (1-30)"),
    include_confidence: bool = Query(True, description="Include confidence intervals"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Prediksi BOR menggunakan model SARIMA yang sudah di-training - Public endpoint
    
    Mengembalikan:
    - Prediksi BOR harian
    - Confidence intervals  
    - Interpretasi dan rekomendasi
    - Warning untuk BOR tinggi/rendah
    """
    try:
        logger.info(f"BOR prediction requested for {days_ahead} days")
        
        # Check if model is trained
        if not sarima_predictor.fitted_model:
            raise HTTPException(
                status_code=400,
                detail="Model belum di-training. Silakan training model terlebih dahulu."
            )
        
        # Generate predictions
        prediction_result = sarima_predictor.predict(
            steps=days_ahead, 
            return_conf_int=include_confidence
        )
        
        # Prepare response sesuai schema
        response = {
            "status": "success",
            "forecast_period": days_ahead,
            "predictions": {
                "values": prediction_result['predictions'],
                "dates": prediction_result['forecast_dates'],
                "confidence_interval": prediction_result.get('confidence_interval', {}),
                "average_predicted_bor": prediction_result['interpretation']['average_predicted_bor']
            },
            "interpretation": prediction_result['interpretation'],
            "model_performance": {
                "last_training_mape": sarima_predictor.performance_metrics.get('mape', 0),
                "meets_journal_criteria": sarima_predictor.performance_metrics.get('mape', 100) < 10,
                "model_parameters": {
                    "order": sarima_predictor.order,
                    "seasonal_order": sarima_predictor.seasonal_order
                }
            },
            "clinical_alerts": {
                "high_occupancy_warning": prediction_result['interpretation']['warnings']['overutilization_risk'],
                "low_occupancy_warning": prediction_result['interpretation']['warnings']['underutilization_risk'],
                "recommendations": prediction_result['interpretation']['recommendations']
            }
        }
        
        logger.info(f"Prediction completed. Average BOR: {response['predictions']['average_predicted_bor']:.1f}%")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in BOR prediction: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating predictions: {str(e)}"
        )

@router.get("/diagnostics")
async def get_model_diagnostics(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Diagnostik lengkap model SARIMA
    
    Mencakup:
    - Uji residual (Ljung-Box test)
    - Statistik model (AIC, BIC, Log-likelihood)
    - Parameter significance
    - Model summary
    """
    try:
        if not sarima_predictor.fitted_model:
            raise HTTPException(
                status_code=400,
                detail="Model belum di-training"
            )
        
        # Get comprehensive model summary
        model_summary = sarima_predictor.get_model_summary()
        
        # Additional diagnostics
        fitted_model = sarima_predictor.fitted_model
        
        diagnostics = {
            "model_identification": {
                "order": model_summary['model_info']['order'],
                "seasonal_order": model_summary['model_info']['seasonal_order'],
                "methodology": "Box-Jenkins SARIMA",
                "estimation_method": "Maximum Likelihood Estimation (MLE)"
            },
            "model_statistics": {
                "aic": model_summary['model_info']['aic'],
                "bic": model_summary['model_info']['bic'],
                "log_likelihood": model_summary['model_info']['log_likelihood'],
                "parameters_count": len(fitted_model.params)
            },
            "residual_diagnostics": model_summary.get('diagnostics', {}),
            "performance_metrics": model_summary.get('performance_metrics', {}),
            "data_information": model_summary.get('data_info', {}),
            "model_validation": {
                "converged": fitted_model.mle_retvals.get('converged', False),
                "white_noise_residuals": model_summary.get('diagnostics', {}).get('ljung_box_test', {}).get('white_noise', False),
                "meets_journal_standards": model_summary.get('performance_metrics', {}).get('mape', 100) < 10
            }
        }
        
        return diagnostics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting model diagnostics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving diagnostics: {str(e)}"
        )

@router.get("/performance")
async def get_model_performance(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Evaluasi performa model sesuai metrik jurnal
    
    Metrik evaluasi:
    - RMSE (Root Mean Square Error)
    - MAE (Mean Absolute Error)
    - MAPE (Mean Absolute Percentage Error) - Target < 10%
    - R-squared
    """
    try:
        if not sarima_predictor.fitted_model or not sarima_predictor.performance_metrics:
            raise HTTPException(
                status_code=400,
                detail="Model belum di-training atau belum dievaluasi"
            )
        
        metrics = sarima_predictor.performance_metrics
        
        performance_report = {
            "evaluation_metrics": {
                "rmse": {
                    "value": metrics.get('rmse', 0),
                    "description": "Root Mean Square Error",
                    "interpretation": "Semakin kecil semakin baik"
                },
                "mae": {
                    "value": metrics.get('mae', 0), 
                    "description": "Mean Absolute Error",
                    "interpretation": "Rata-rata kesalahan absolut"
                },
                "mape": {
                    "value": metrics.get('mape', 0),
                    "description": "Mean Absolute Percentage Error (%)",
                    "interpretation": "Target < 10% sesuai jurnal",
                    "meets_target": metrics.get('mape', 100) < 10
                },
                "r_squared": {
                    "value": metrics.get('r_squared', 0),
                    "description": "Coefficient of Determination",
                    "interpretation": "Proporsi varians yang dijelaskan model"
                }
            },
            "journal_compliance": {
                "target_mape": "< 10%",
                "achieved_mape": f"{metrics.get('mape', 0):.2f}%",
                "meets_criteria": metrics.get('mape', 100) < 10,
                "performance_level": self._get_performance_level(metrics.get('mape', 100))
            },
            "model_quality": {
                "sample_size": metrics.get('n_observations', 0),
                "data_quality": "Good" if metrics.get('n_observations', 0) > 60 else "Limited",
                "prediction_reliability": "High" if metrics.get('mape', 100) < 5 else "Medium" if metrics.get('mape', 100) < 10 else "Low"
            },
            "recommendations": self._get_performance_recommendations(metrics)
        }
        
        return performance_report
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting performance metrics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving performance metrics: {str(e)}"
        )

@router.post("/retrain")
async def retrain_model(
    retrain_request: SARIMATrainingRequest = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Re-training model dengan data terbaru
    Digunakan untuk update model berkala
    """
    try:
        logger.info(f"Model retraining requested by {current_user.username}")
        
        # Reset existing model
        sarima_predictor.fitted_model = None
        sarima_predictor.performance_metrics = {}
        sarima_predictor.diagnostics = {}
        
        # Call training endpoint
        return await train_sarima_model(retrain_request, db, current_user)
        
    except Exception as e:
        logger.error(f"Error retraining model: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retraining model: {str(e)}"
        )

@router.get("/status")
async def get_model_status() -> Dict[str, Any]:
    """
    Status model SARIMA saat ini - Public endpoint untuk status check
    """
    try:
        is_trained = sarima_predictor.fitted_model is not None
        
        status = {
            "model_trained": is_trained,
            "last_training": None,  # Could be stored in database
            "model_parameters": {
                "order": sarima_predictor.order,
                "seasonal_order": sarima_predictor.seasonal_order
            } if is_trained else None,
            "performance_summary": {
                "mape": sarima_predictor.performance_metrics.get('mape', 0),
                "meets_journal_criteria": sarima_predictor.performance_metrics.get('mape', 100) < 10
            } if is_trained else None,
            "ready_for_prediction": is_trained
        }
        
        return status
        
    except Exception as e:
        logger.error(f"Error getting model status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving model status: {str(e)}"
        )

def _get_performance_level(mape: float) -> str:
    """Helper function to categorize model performance"""
    if mape < 5:
        return "Excellent"
    elif mape < 10:
        return "Good"
    elif mape < 15:
        return "Acceptable"
    else:
        return "Needs Improvement"

def _get_performance_recommendations(metrics: Dict[str, float]) -> List[str]:
    """Helper function to generate performance recommendations"""
    recommendations = []
    mape = metrics.get('mape', 100)
    
    if mape < 5:
        recommendations.append("Model memiliki akurasi sangat tinggi")
        recommendations.append("Pertahankan kualitas data dan frekuensi retraining")
    elif mape < 10:
        recommendations.append("Model memenuhi standar jurnal (MAPE < 10%)")
        recommendations.append("Lakukan monitoring berkala")
    else:
        recommendations.append("Model perlu improvement untuk mencapai target jurnal")
        recommendations.append("Pertimbangkan penambahan data training")
        recommendations.append("Evaluasi kualitas data input")
        recommendations.append("Coba optimasi parameter model")
    
    return recommendations