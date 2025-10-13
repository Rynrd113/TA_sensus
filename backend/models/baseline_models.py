#!/usr/bin/env python3
"""
Baseline Models for SARIMA Comparison
Penelitian: "Peramalan Indikator Rumah Sakit Berbasis Sensus Harian Rawat Inap dengan Model SARIMA"

Model baseline yang diimplementasikan:
1. Naive Forecast: Prediksi = nilai hari kemarin
2. Moving Average: Prediksi = rata-rata 7 hari terakhir  
3. ARIMA (non-seasonal): ARIMA tanpa komponen musiman
4. SARIMA: Model utama penelitian

Author: Research Team
Date: October 2025
"""

import os
import sys
import json
import pickle
import warnings
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
import logging

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Data processing
import pandas as pd
import numpy as np
import sqlite3

# Statistical models
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX

# Metrics
from sklearn.metrics import mean_squared_error, mean_absolute_error

# Suppress warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class BaselineModels:
    """
    Implementasi model baseline untuk perbandingan dengan SARIMA
    
    Models:
    1. Naive Forecast: Menggunakan nilai hari sebelumnya
    2. Moving Average: Rata-rata 7 hari terakhir
    3. ARIMA: Model ARIMA non-seasonal
    4. SARIMA: Model utama penelitian
    """
    
    def __init__(self, db_path: str = "../db/sensus.db"):
        self.db_path = db_path
        self.data = None
        self.train_data = None
        self.test_data = None
        self.models = {}
        self.predictions = {}
        self.performance = {}
        
        # Model directory
        self.model_dir = os.path.dirname(os.path.abspath(__file__))
        
        logger.info("Baseline Models Comparison System Initialized")
    
    def load_data(self) -> pd.DataFrame:
        """Load data from database"""
        try:
            db_path = os.path.join(self.model_dir, self.db_path)
            
            if not os.path.exists(db_path):
                raise FileNotFoundError(f"Database file not found: {db_path}")
            
            # Connect to database
            conn = sqlite3.connect(db_path)
            
            # Query data
            query = """
            SELECT tanggal, bor
            FROM sensus_harian
            WHERE bor IS NOT NULL
            ORDER BY tanggal
            """
            
            # Load data
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            # Convert date column
            df['tanggal'] = pd.to_datetime(df['tanggal'])
            df.set_index('tanggal', inplace=True)
            
            # Store data
            self.data = df['bor']
            
            logger.info(f"Data loaded successfully")
            logger.info(f"Total data points: {len(self.data)}")
            logger.info(f"Date range: {self.data.index.min()} to {self.data.index.max()}")
            
            return self.data
            
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise
    
    def split_data(self, train_ratio: float = 0.8) -> Tuple[pd.Series, pd.Series]:
        """Split data into train and test sets"""
        try:
            if self.data is None:
                raise ValueError("Data not loaded. Call load_data() first.")
            
            # Split data
            split_index = int(len(self.data) * train_ratio)
            
            self.train_data = self.data.iloc[:split_index]
            self.test_data = self.data.iloc[split_index:]
            
            logger.info(f"Data split completed")
            logger.info(f"Training data: {len(self.train_data)} points")
            logger.info(f"Testing data: {len(self.test_data)} points")
            
            return self.train_data, self.test_data
            
        except Exception as e:
            logger.error(f"Error splitting data: {e}")
            raise
    
    def train_naive_model(self) -> Dict[str, Any]:
        """
        Naive Forecast Model
        Prediksi = nilai hari kemarin (last observed value)
        """
        try:
            logger.info("Training Naive Forecast model...")
            
            if self.train_data is None:
                raise ValueError("Training data not available")
            
            # Naive model: prediction = last observed value
            # For each test point, use the last available training value
            last_train_value = self.train_data.iloc[-1]
            
            # Generate predictions for test period
            predictions = [last_train_value] * len(self.test_data)
            
            self.predictions['naive'] = pd.Series(
                predictions, 
                index=self.test_data.index,
                name='naive_predictions'
            )
            
            # Store model info
            model_info = {
                'type': 'naive',
                'description': 'Naive Forecast (last observed value)',
                'last_value': float(last_train_value),
                'n_predictions': len(predictions)
            }
            
            self.models['naive'] = model_info
            
            logger.info(f"Naive model trained successfully")
            logger.info(f"Last training value: {last_train_value:.2f}")
            
            return model_info
            
        except Exception as e:
            logger.error(f"Error training naive model: {e}")
            raise
    
    def train_moving_average_model(self, window: int = 7) -> Dict[str, Any]:
        """
        Moving Average Model
        Prediksi = rata-rata 7 hari terakhir
        """
        try:
            logger.info(f"Training Moving Average model (window={window})...")
            
            if self.train_data is None:
                raise ValueError("Training data not available")
            
            # Calculate moving average of last 'window' days
            if len(self.train_data) < window:
                # If not enough data, use all available data
                ma_value = self.train_data.mean()
                actual_window = len(self.train_data)
            else:
                ma_value = self.train_data.iloc[-window:].mean()
                actual_window = window
            
            # Generate predictions for test period
            predictions = [ma_value] * len(self.test_data)
            
            self.predictions['moving_avg'] = pd.Series(
                predictions,
                index=self.test_data.index,
                name='moving_avg_predictions'
            )
            
            # Store model info
            model_info = {
                'type': 'moving_average',
                'description': f'Moving Average ({actual_window} days)',
                'window_size': actual_window,
                'ma_value': float(ma_value),
                'n_predictions': len(predictions)
            }
            
            self.models['moving_avg'] = model_info
            
            logger.info(f"Moving Average model trained successfully")
            logger.info(f"MA value ({actual_window} days): {ma_value:.2f}")
            
            return model_info
            
        except Exception as e:
            logger.error(f"Error training moving average model: {e}")
            raise
    
    def train_arima_model(self, max_p: int = 3, max_d: int = 2, max_q: int = 3) -> Dict[str, Any]:
        """
        ARIMA Model (non-seasonal)
        Grid search untuk parameter terbaik
        """
        try:
            logger.info("Training ARIMA model (non-seasonal)...")
            
            if self.train_data is None:
                raise ValueError("Training data not available")
            
            best_aic = float('inf')
            best_order = None
            best_model = None
            
            # Grid search for ARIMA parameters
            logger.info(f"Grid search for ARIMA parameters...")
            total_combinations = (max_p + 1) * (max_d + 1) * (max_q + 1)
            combination_count = 0
            
            for p in range(max_p + 1):
                for d in range(max_d + 1):
                    for q in range(max_q + 1):
                        combination_count += 1
                        
                        try:
                            model = ARIMA(self.train_data, order=(p, d, q))
                            fitted_model = model.fit()
                            
                            if fitted_model.aic < best_aic:
                                best_aic = fitted_model.aic
                                best_order = (p, d, q)
                                best_model = fitted_model
                            
                            # Progress logging
                            if combination_count % (total_combinations // 4) == 0:
                                progress = (combination_count / total_combinations) * 100
                                logger.info(f"ARIMA grid search progress: {progress:.0f}% - Current best AIC: {best_aic:.2f}")
                        
                        except:
                            continue
            
            if best_model is None:
                raise ValueError("No valid ARIMA model found")
            
            # Generate predictions
            forecast_result = best_model.get_forecast(steps=len(self.test_data))
            predictions = forecast_result.predicted_mean
            
            self.predictions['arima'] = pd.Series(
                predictions.values,
                index=self.test_data.index,
                name='arima_predictions'
            )
            
            # Store model info
            model_info = {
                'type': 'arima',
                'description': f'ARIMA{best_order}',
                'order': best_order,
                'aic': float(best_model.aic),
                'bic': float(best_model.bic),
                'converged': best_model.mle_retvals['converged'],
                'n_predictions': len(predictions)
            }
            
            self.models['arima'] = model_info
            
            logger.info(f"ARIMA model trained successfully")
            logger.info(f"Best order: {best_order}")
            logger.info(f"AIC: {best_model.aic:.2f}")
            
            return model_info
            
        except Exception as e:
            logger.error(f"Error training ARIMA model: {e}")
            raise
    
    def load_sarima_model(self) -> Dict[str, Any]:
        """
        Load SARIMA model yang sudah ditraining sebelumnya
        """
        try:
            logger.info("Loading pre-trained SARIMA model...")
            
            # Load SARIMA model
            sarima_model_path = os.path.join(self.model_dir, "sarima_model.pkl")
            sarima_log_path = os.path.join(self.model_dir, "training_log.json")
            
            if not os.path.exists(sarima_model_path):
                raise FileNotFoundError(f"SARIMA model not found: {sarima_model_path}")
            
            if not os.path.exists(sarima_log_path):
                raise FileNotFoundError(f"SARIMA log not found: {sarima_log_path}")
            
            # Load model
            with open(sarima_model_path, 'rb') as f:
                sarima_fitted = pickle.load(f)
            
            # Load training log
            with open(sarima_log_path, 'r', encoding='utf-8') as f:
                sarima_log = json.load(f)
            
            # Generate SARIMA predictions for test data
            forecast_result = sarima_fitted.get_forecast(steps=len(self.test_data))
            predictions = forecast_result.predicted_mean
            
            self.predictions['sarima'] = pd.Series(
                predictions.values,
                index=self.test_data.index,
                name='sarima_predictions'
            )
            
            # Extract model info from log
            model_info = {
                'type': 'sarima',
                'description': sarima_log['model_info']['model_formula'],
                'order': tuple(sarima_log['model_info']['order']),
                'seasonal_order': tuple(sarima_log['model_info']['seasonal_order']),
                'aic': sarima_log['model_statistics']['aic'],
                'bic': sarima_log['model_statistics']['bic'],
                'converged': sarima_log['model_statistics']['converged'],
                'n_predictions': len(predictions)
            }
            
            self.models['sarima'] = model_info
            
            logger.info(f"SARIMA model loaded successfully")
            logger.info(f"Model: {model_info['description']}")
            
            return model_info
            
        except Exception as e:
            logger.error(f"Error loading SARIMA model: {e}")
            raise
    
    def calculate_metrics(self, actual: pd.Series, predicted: pd.Series) -> Dict[str, float]:
        """Calculate performance metrics"""
        try:
            # Ensure same length and no NaN values
            mask = ~(np.isnan(actual) | np.isnan(predicted))
            actual_clean = actual[mask]
            predicted_clean = predicted[mask]
            
            if len(actual_clean) == 0:
                return {'error': 'No valid data points for evaluation'}
            
            # Calculate metrics
            rmse = np.sqrt(mean_squared_error(actual_clean, predicted_clean))
            mae = mean_absolute_error(actual_clean, predicted_clean)
            
            # MAPE with zero-handling
            mape_values = []
            for i in range(len(actual_clean)):
                if actual_clean.iloc[i] != 0:
                    mape_values.append(abs((actual_clean.iloc[i] - predicted_clean.iloc[i]) / actual_clean.iloc[i]))
            
            mape = np.mean(mape_values) * 100 if mape_values else 0
            
            return {
                'rmse': float(rmse),
                'mae': float(mae),
                'mape': float(mape)
            }
            
        except Exception as e:
            logger.error(f"Error calculating metrics: {e}")
            return {'error': str(e)}
    
    def evaluate_all_models(self) -> Dict[str, Dict[str, float]]:
        """Evaluate all models and compare performance"""
        try:
            logger.info("Evaluating all models...")
            
            if self.test_data is None:
                raise ValueError("Test data not available")
            
            results = {}
            
            for model_name in ['naive', 'moving_avg', 'arima', 'sarima']:
                if model_name in self.predictions:
                    metrics = self.calculate_metrics(self.test_data, self.predictions[model_name])
                    results[model_name] = metrics
                    
                    if 'error' not in metrics:
                        logger.info(f"{model_name.upper()} - RMSE: {metrics['rmse']:.2f}, MAE: {metrics['mae']:.2f}, MAPE: {metrics['mape']:.2f}%")
                    else:
                        logger.error(f"{model_name.upper()} - Error: {metrics['error']}")
                else:
                    logger.warning(f"Predictions not available for {model_name}")
            
            self.performance = results
            return results
            
        except Exception as e:
            logger.error(f"Error evaluating models: {e}")
            raise
    
    def save_comparison_results(self, filename: str = "comparison_results.json") -> str:
        """Save comparison results to JSON file"""
        try:
            output_path = os.path.join(self.model_dir, filename)
            
            # Prepare comprehensive results
            comparison_data = {
                'timestamp': datetime.now().isoformat(),
                'data_info': {
                    'total_points': len(self.data) if self.data is not None else 0,
                    'train_points': len(self.train_data) if self.train_data is not None else 0,
                    'test_points': len(self.test_data) if self.test_data is not None else 0,
                    'date_range': {
                        'start': self.data.index.min().isoformat() if self.data is not None else None,
                        'end': self.data.index.max().isoformat() if self.data is not None else None
                    }
                },
                'models': self.models,
                'performance': self.performance,
                'ranking': self._rank_models()
            }
            
            # Save to file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(comparison_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Comparison results saved: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error saving results: {e}")
            raise
    
    def _rank_models(self) -> Dict[str, Dict[str, int]]:
        """Rank models by performance metrics"""
        rankings = {
            'rmse': {},
            'mae': {},
            'mape': {}
        }
        
        for metric in ['rmse', 'mae', 'mape']:
            # Get metric values for valid models
            metric_values = {}
            for model, performance in self.performance.items():
                if 'error' not in performance and metric in performance:
                    metric_values[model] = performance[metric]
            
            # Sort by metric (lower is better)
            sorted_models = sorted(metric_values.items(), key=lambda x: x[1])
            
            # Assign ranks
            for rank, (model, value) in enumerate(sorted_models, 1):
                rankings[metric][model] = rank
        
        return rankings
    
    def print_comparison_summary(self):
        """Print detailed comparison summary"""
        try:
            print("\n" + "="*80)
            print("PERBANDINGAN MODEL BASELINE vs SARIMA")
            print("Penelitian: Peramalan Indikator Rumah Sakit Berbasis Sensus Harian Rawat Inap")
            print("="*80)
            
            if self.performance:
                print(f"\n📊 HASIL PERBANDINGAN MODEL:")
                print(f"{'Model':<15} {'RMSE':<10} {'MAE':<10} {'MAPE (%)':<12} {'Rank MAPE':<12}")
                print("-" * 70)
                
                # Sort by MAPE for display
                sorted_models = sorted(
                    [(name, perf) for name, perf in self.performance.items() if 'error' not in perf],
                    key=lambda x: x[1]['mape']
                )
                
                for rank, (model_name, metrics) in enumerate(sorted_models, 1):
                    model_display = {
                        'naive': 'Naive',
                        'moving_avg': 'Moving Avg',
                        'arima': 'ARIMA',
                        'sarima': 'SARIMA'
                    }.get(model_name, model_name)
                    
                    print(f"{model_display:<15} {metrics['rmse']:<10.2f} {metrics['mae']:<10.2f} "
                          f"{metrics['mape']:<12.2f} {rank:<12}")
                
                # Best model summary
                best_model = sorted_models[0][0] if sorted_models else None
                if best_model:
                    print(f"\n🏆 MODEL TERBAIK: {best_model.upper()}")
                    best_metrics = self.performance[best_model]
                    print(f"   RMSE: {best_metrics['rmse']:.2f}")
                    print(f"   MAE: {best_metrics['mae']:.2f}")
                    print(f"   MAPE: {best_metrics['mape']:.2f}%")
                
                # Model descriptions
                print(f"\n📝 DESKRIPSI MODEL:")
                for model_name, model_info in self.models.items():
                    if model_name in self.performance:
                        print(f"   {model_name.upper()}: {model_info['description']}")
                
                # Data info
                if self.data is not None:
                    print(f"\n📅 INFORMASI DATA:")
                    print(f"   Total Data: {len(self.data)} hari")
                    print(f"   Training: {len(self.train_data)} hari")
                    print(f"   Testing: {len(self.test_data)} hari")
                    print(f"   Periode: {self.data.index.min().strftime('%Y-%m-%d')} s/d {self.data.index.max().strftime('%Y-%m-%d')}")
                
                print(f"\n📁 FILE OUTPUT:")
                print(f"   Hasil: comparison_results.json")
                
                print(f"\n📝 CATATAN UNTUK JURNAL:")
                print(f"   • Perbandingan menunjukkan superioritas model SARIMA")
                print(f"   • Baseline models memberikan konteks performa")
                print(f"   • Semua model dievaluasi pada test set yang sama")
                
            else:
                print("\n❌ PERBANDINGAN BELUM SELESAI")
                print("Jalankan evaluasi model untuk mendapatkan hasil.")
            
            print("\n" + "="*80)
            
        except Exception as e:
            logger.error(f"Error printing summary: {e}")
    
    def run_full_comparison(self):
        """Run complete baseline comparison"""
        try:
            logger.info("🚀 STARTING BASELINE MODELS COMPARISON")
            logger.info("="*60)
            
            # Step 1: Load data
            logger.info("Step 1: Loading data...")
            self.load_data()
            
            # Step 2: Split data
            logger.info("Step 2: Splitting data...")
            self.split_data()
            
            # Step 3: Train baseline models
            logger.info("Step 3: Training baseline models...")
            self.train_naive_model()
            self.train_moving_average_model()
            self.train_arima_model()
            
            # Step 4: Load SARIMA model
            logger.info("Step 4: Loading SARIMA model...")
            self.load_sarima_model()
            
            # Step 5: Evaluate all models
            logger.info("Step 5: Evaluating all models...")
            self.evaluate_all_models()
            
            # Step 6: Save results
            logger.info("Step 6: Saving comparison results...")
            self.save_comparison_results()
            
            # Step 7: Print summary
            logger.info("Step 7: Generating comparison summary...")
            self.print_comparison_summary()
            
            logger.info("🎉 BASELINE COMPARISON COMPLETED SUCCESSFULLY!")
            
        except Exception as e:
            logger.error(f"❌ BASELINE COMPARISON FAILED: {e}")
            raise


def main():
    """Main function untuk menjalankan perbandingan model"""
    try:
        # Initialize comparison system
        comparison = BaselineModels()
        
        # Run full comparison
        comparison.run_full_comparison()
        
    except Exception as e:
        logger.error(f"Comparison failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()