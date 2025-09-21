"""
SARIMA Model Implementation for Hospital Bed Occupancy Rate Prediction
Sesuai dengan penelitian: "Peramalan Indikator Rumah Sakit Berbasis Sensus Harian Rawat Inap dengan Model SARIMA"

Implementasi menggunakan metodologi Box-Jenkins:
1. Identifikasi orde model dengan plot ACF dan PACF
2. Estimasi parameter menggunakan Maximum Likelihood Estimation (MLE)  
3. Uji diagnostik residual untuk memastikan white noise
4. Evaluasi performa dengan metrik RMSE, MAE, MAPE
"""

import pandas as pd
import numpy as np
import warnings
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
import logging

# Statistical models
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import adfuller, acf, pacf
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.seasonal import seasonal_decompose

# Visualization
import matplotlib.pyplot as plt
import seaborn as sns

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SARIMAPredictor:
    """
    SARIMA Model untuk prediksi BOR (Bed Occupancy Rate)
    
    Model: SARIMA(p,d,q)(P,D,Q)s
    - p: orde autoregresif (AR)
    - d: orde differencing (I) 
    - q: orde moving average (MA)
    - P, D, Q: komponen musiman
    - s: periode musiman (7 untuk pola mingguan)
    """
    
    def __init__(self):
        self.model = None
        self.fitted_model = None
        self.data_series = None
        self.train_data = None
        self.test_data = None
        
        # Default parameters berdasarkan penelitian
        self.order = (1, 1, 1)  # (p,d,q)
        self.seasonal_order = (1, 1, 1, 7)  # (P,D,Q,s) - pola mingguan
        
        # Model diagnostics
        self.diagnostics = {}
        self.performance_metrics = {}
        
    def prepare_data(self, data: List[Dict], target_column: str = 'bor') -> pd.Series:
        """
        Persiapkan data SHRI untuk analisis time series
        
        Args:
            data: List of dictionaries dengan kolom tanggal dan target
            target_column: Kolom target untuk prediksi (default: 'bor')
            
        Returns:
            pd.Series: Data time series yang sudah diproses
        """
        try:
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Ensure datetime index
            if 'tanggal' in df.columns:
                df['tanggal'] = pd.to_datetime(df['tanggal'])
                df.set_index('tanggal', inplace=True)
            
            # Sort by date
            df = df.sort_index()
            
            # Handle missing values
            if target_column not in df.columns:
                raise ValueError(f"Column '{target_column}' not found in data")
                
            series = df[target_column].copy()
            
            # Remove outliers using IQR method
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            # Replace outliers with median
            median_value = series.median()
            series = series.where(
                (series >= lower_bound) & (series <= upper_bound), 
                median_value
            )
            
            # Forward fill missing values
            series = series.fillna(method='ffill')
            
            # Backward fill any remaining
            series = series.fillna(method='bfill')
            
            self.data_series = series
            logger.info(f"Data prepared successfully. Shape: {series.shape}")
            logger.info(f"Date range: {series.index.min()} to {series.index.max()}")
            
            return series
            
        except Exception as e:
            logger.error(f"Error preparing data: {str(e)}")
            raise
    
    def check_stationarity(self, data: pd.Series = None) -> Dict[str, Any]:
        """
        Uji stasioneritas menggunakan Augmented Dickey-Fuller Test
        Sesuai metodologi penelitian
        
        Returns:
            Dict: Hasil uji stasioneritas
        """
        if data is None:
            data = self.data_series
            
        if data is None:
            raise ValueError("No data available for stationarity test")
        
        # Perform ADF test
        result = adfuller(data.dropna())
        
        adf_result = {
            'adf_statistic': result[0],
            'p_value': result[1],
            'used_lags': result[2],
            'nobs': result[3],
            'critical_values': result[4],
            'is_stationary': result[1] <= 0.05,
            'conclusion': 'Stationary' if result[1] <= 0.05 else 'Non-stationary'
        }
        
        logger.info(f"ADF Test Results:")
        logger.info(f"  ADF Statistic: {adf_result['adf_statistic']:.6f}")
        logger.info(f"  p-value: {adf_result['p_value']:.6f}")
        logger.info(f"  Conclusion: {adf_result['conclusion']}")
        
        return adf_result
    
    def plot_acf_pacf(self, data: pd.Series = None, lags: int = 40) -> Dict[str, Any]:
        """
        Plot ACF dan PACF untuk identifikasi orde model
        Sesuai metodologi Box-Jenkins
        """
        if data is None:
            data = self.data_series
            
        if data is None:
            raise ValueError("No data available for ACF/PACF analysis")
        
        # Calculate ACF and PACF
        acf_values = acf(data.dropna(), nlags=lags)
        pacf_values = pacf(data.dropna(), nlags=lags)
        
        return {
            'acf_values': acf_values.tolist(),
            'pacf_values': pacf_values.tolist(),
            'lags': list(range(lags + 1))
        }
    
    def optimize_parameters(self, data: pd.Series = None, 
                          max_p: int = 3, max_d: int = 2, max_q: int = 3,
                          max_P: int = 2, max_D: int = 1, max_Q: int = 2) -> Dict[str, Any]:
        """
        Optimasi parameter SARIMA menggunakan grid search
        Evaluasi berdasarkan AIC (Akaike Information Criterion)
        """
        if data is None:
            data = self.data_series
            
        if data is None:
            raise ValueError("No data available for parameter optimization")
        
        best_aic = float('inf')
        best_params = None
        results = []
        
        logger.info("Starting SARIMA parameter optimization...")
        
        for p in range(max_p + 1):
            for d in range(max_d + 1):
                for q in range(max_q + 1):
                    for P in range(max_P + 1):
                        for D in range(max_D + 1):
                            for Q in range(max_Q + 1):
                                try:
                                    model = SARIMAX(
                                        data,
                                        order=(p, d, q),
                                        seasonal_order=(P, D, Q, 7),
                                        enforce_stationarity=False,
                                        enforce_invertibility=False
                                    )
                                    
                                    fitted_model = model.fit(disp=False)
                                    aic = fitted_model.aic
                                    
                                    results.append({
                                        'order': (p, d, q),
                                        'seasonal_order': (P, D, Q, 7),
                                        'aic': aic
                                    })
                                    
                                    if aic < best_aic:
                                        best_aic = aic
                                        best_params = {
                                            'order': (p, d, q),
                                            'seasonal_order': (P, D, Q, 7),
                                            'aic': aic
                                        }
                                        
                                except:
                                    continue
        
        if best_params:
            self.order = best_params['order']
            self.seasonal_order = best_params['seasonal_order']
            logger.info(f"Best parameters found: {best_params}")
        
        return {
            'best_params': best_params,
            'all_results': sorted(results, key=lambda x: x['aic'])[:10]  # Top 10
        }
    
    def fit_model(self, data: pd.Series = None, optimize: bool = True) -> Dict[str, Any]:
        """
        Fit model SARIMA menggunakan Maximum Likelihood Estimation
        Sesuai metodologi penelitian
        """
        if data is None:
            data = self.data_series
            
        if data is None:
            raise ValueError("No data available for model fitting")
        
        try:
            # Optimize parameters if requested
            if optimize:
                optimization_results = self.optimize_parameters(data)
                logger.info("Parameter optimization completed")
            
            # Fit SARIMA model
            logger.info(f"Fitting SARIMA{self.order}x{self.seasonal_order} model...")
            
            self.model = SARIMAX(
                data,
                order=self.order,
                seasonal_order=self.seasonal_order,
                enforce_stationarity=False,
                enforce_invertibility=False
            )
            
            self.fitted_model = self.model.fit(
                disp=False,
                method='lbfgs',  # Limited-memory BFGS
                maxiter=1000
            )
            
            # Store model information
            model_info = {
                'order': self.order,
                'seasonal_order': self.seasonal_order,
                'aic': self.fitted_model.aic,
                'bic': self.fitted_model.bic,
                'log_likelihood': self.fitted_model.llf,
                'converged': self.fitted_model.mle_retvals['converged']
            }
            
            logger.info(f"Model fitted successfully. AIC: {model_info['aic']:.2f}")
            
            return model_info
            
        except Exception as e:
            logger.error(f"Error fitting model: {str(e)}")
            raise
    
    def diagnostic_tests(self) -> Dict[str, Any]:
        """
        Uji diagnostik residual untuk validasi model
        - Ljung-Box test untuk white noise
        - Residual analysis
        """
        if not self.fitted_model:
            raise ValueError("Model has not been fitted yet")
        
        residuals = self.fitted_model.resid
        
        # Ljung-Box test for white noise
        ljung_box = acorr_ljungbox(residuals, lags=10, return_df=True)
        
        # Basic residual statistics
        residual_stats = {
            'mean': float(residuals.mean()),
            'std': float(residuals.std()),
            'skewness': float(residuals.skew()),
            'kurtosis': float(residuals.kurtosis())
        }
        
        # Normality test (simplified)
        residual_normalized = (residuals - residuals.mean()) / residuals.std()
        
        diagnostics = {
            'ljung_box_test': {
                'statistics': ljung_box['lb_stat'].tolist(),
                'p_values': ljung_box['lb_pvalue'].tolist(),
                'white_noise': all(ljung_box['lb_pvalue'] > 0.05)  # Simplified check
            },
            'residual_statistics': residual_stats,
            'residuals': residuals.tolist()
        }
        
        self.diagnostics = diagnostics
        return diagnostics
    
    def evaluate_performance(self, actual: pd.Series, predicted: pd.Series) -> Dict[str, float]:
        """
        Evaluasi performa model menggunakan metrik sesuai jurnal:
        - RMSE (Root Mean Square Error)
        - MAE (Mean Absolute Error) 
        - MAPE (Mean Absolute Percentage Error)
        """
        # Ensure same length
        min_len = min(len(actual), len(predicted))
        actual = actual.iloc[:min_len]
        predicted = predicted.iloc[:min_len]
        
        # Remove any NaN values
        mask = ~(np.isnan(actual) | np.isnan(predicted))
        actual = actual[mask]
        predicted = predicted[mask]
        
        if len(actual) == 0:
            return {'error': 'No valid data points for evaluation'}
        
        # Calculate metrics
        rmse = np.sqrt(np.mean((actual - predicted) ** 2))
        mae = np.mean(np.abs(actual - predicted))
        
        # MAPE with handling for zero values
        mape_values = []
        for i in range(len(actual)):
            if actual.iloc[i] != 0:
                mape_values.append(abs((actual.iloc[i] - predicted.iloc[i]) / actual.iloc[i]))
        
        mape = np.mean(mape_values) * 100 if mape_values else 0
        
        # Additional metrics
        mse = np.mean((actual - predicted) ** 2)
        r_squared = 1 - (np.sum((actual - predicted) ** 2) / np.sum((actual - actual.mean()) ** 2))
        
        metrics = {
            'rmse': float(rmse),
            'mae': float(mae),
            'mape': float(mape),
            'mse': float(mse),
            'r_squared': float(r_squared),
            'n_observations': len(actual)
        }
        
        self.performance_metrics = metrics
        
        logger.info(f"Performance Metrics:")
        logger.info(f"  RMSE: {metrics['rmse']:.4f}")
        logger.info(f"  MAE: {metrics['mae']:.4f}")
        logger.info(f"  MAPE: {metrics['mape']:.2f}%")
        
        # Check if meets journal criteria (MAPE < 10%)
        if metrics['mape'] < 10:
            logger.info("✓ Model meets journal performance criteria (MAPE < 10%)")
        else:
            logger.warning("⚠ Model does not meet journal performance criteria (MAPE >= 10%)")
        
        return metrics
    
    def predict(self, steps: int = 7, return_conf_int: bool = True) -> Dict[str, Any]:
        """
        Prediksi BOR untuk periode mendatang
        
        Args:
            steps: Jumlah hari prediksi ke depan
            return_conf_int: Return confidence interval atau tidak
            
        Returns:
            Dict: Hasil prediksi dengan confidence interval
        """
        if not self.fitted_model:
            raise ValueError("Model has not been fitted yet")
        
        try:
            # Generate forecast
            forecast_result = self.fitted_model.get_forecast(steps=steps)
            predictions = forecast_result.predicted_mean
            
            result = {
                'predictions': predictions.tolist(),
                'forecast_dates': [
                    (self.data_series.index[-1] + timedelta(days=i+1)).strftime('%Y-%m-%d')
                    for i in range(steps)
                ]
            }
            
            # Add confidence intervals if requested
            if return_conf_int:
                conf_int = forecast_result.conf_int()
                result['confidence_interval'] = {
                    'lower': conf_int.iloc[:, 0].tolist(),
                    'upper': conf_int.iloc[:, 1].tolist()
                }
            
            # Add interpretation
            result['interpretation'] = self._interpret_predictions(predictions.tolist())
            
            logger.info(f"Generated {steps}-day forecast successfully")
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating predictions: {str(e)}")
            raise
    
    def _interpret_predictions(self, predictions: List[float]) -> Dict[str, Any]:
        """
        Interpretasi hasil prediksi sesuai standar rumah sakit
        """
        high_bor = [p for p in predictions if p > 85]  # Overutilization
        low_bor = [p for p in predictions if p < 60]   # Underutilization
        optimal_bor = [p for p in predictions if 60 <= p <= 85]  # Optimal range
        
        return {
            'high_risk_days': len(high_bor),
            'low_utilization_days': len(low_bor),
            'optimal_days': len(optimal_bor),
            'average_predicted_bor': float(np.mean(predictions)),
            'warnings': {
                'overutilization_risk': len(high_bor) > 0,
                'underutilization_risk': len(low_bor) > len(predictions) // 2
            },
            'recommendations': self._generate_recommendations(predictions)
        }
    
    def _generate_recommendations(self, predictions: List[float]) -> List[str]:
        """
        Generate recommendations based on predictions
        """
        recommendations = []
        avg_bor = np.mean(predictions)
        
        if avg_bor > 85:
            recommendations.append("Pertimbangkan penambahan kapasitas tempat tidur")
            recommendations.append("Evaluasi discharge planning untuk mempercepat turnover")
            recommendations.append("Monitor antrian pasien masuk")
        elif avg_bor < 60:
            recommendations.append("Evaluasi strategi marketing untuk meningkatkan occupancy")
            recommendations.append("Review efisiensi operasional")
            recommendations.append("Pertimbangkan optimasi jadwal staf")
        else:
            recommendations.append("Pertahankan tingkat occupancy saat ini")
            recommendations.append("Monitor tren untuk deteksi dini perubahan pola")
        
        return recommendations
    
    def get_model_summary(self) -> Dict[str, Any]:
        """
        Ringkasan lengkap model dan performanya
        """
        if not self.fitted_model:
            return {'error': 'Model has not been fitted yet'}
        
        return {
            'model_info': {
                'order': self.order,
                'seasonal_order': self.seasonal_order,
                'aic': float(self.fitted_model.aic),
                'bic': float(self.fitted_model.bic),
                'log_likelihood': float(self.fitted_model.llf)
            },
            'performance_metrics': self.performance_metrics,
            'diagnostics': self.diagnostics,
            'data_info': {
                'total_observations': len(self.data_series) if self.data_series is not None else 0,
                'date_range': {
                    'start': self.data_series.index[0].strftime('%Y-%m-%d') if self.data_series is not None else None,
                    'end': self.data_series.index[-1].strftime('%Y-%m-%d') if self.data_series is not None else None
                }
            }
        }

# Singleton instance for global use
sarima_predictor = SARIMAPredictor()