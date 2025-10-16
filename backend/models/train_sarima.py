#!/usr/bin/env python3
"""
SARIMA Training Pipeline for Hospital Bed Occupancy Rate Prediction
Penelitian: "Peramalan Indikator Rumah Sakit Berbasis Sensus Harian Rawat Inap dengan Model SARIMA"

Script ini mengimplementasikan metodologi Box-Jenkins untuk training model SARIMA:
1. Load data SHRI dari database SQLite
2. Split data 80:20 (train:test)
3. Grid search untuk parameter (p,d,q)(P,D,Q)s
4. Pilih model terbaik berdasarkan AIC
5. Train final model
6. Save model sebagai .pkl
7. Save metrics (RMSE, MAE, MAPE) ke JSON

Author: Research Team
Date: October 2025
"""

import os
import sys
import json
import pickle
import yaml
import warnings
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import logging

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Data processing
import pandas as pd
import numpy as np
import sqlite3

# Statistical models and tests
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import adfuller
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.seasonal import seasonal_decompose

# Metrics
from sklearn.metrics import mean_squared_error, mean_absolute_error

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class SARIMATrainer:
    """
    SARIMA Training Pipeline untuk prediksi BOR (Bed Occupancy Rate)
    
    Implementasi metodologi Box-Jenkins:
    - Grid search untuk optimasi parameter
    - Evaluasi menggunakan AIC/BIC
    - Validasi residual dengan Ljung-Box test
    - Performance metrics: RMSE, MAE, MAPE
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize trainer with configuration"""
        self.config = self._load_config(config_path)
        self.data = None
        self.train_data = None
        self.test_data = None
        self.best_model = None
        self.best_params = None
        self.training_history = []
        self.performance_metrics = {}
        
        # Setup output directory
        self.model_dir = os.path.dirname(os.path.abspath(__file__))
        
        logger.info("SARIMA Training Pipeline Initialized")
        logger.info(f"Configuration loaded from: {config_path}")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
            return config
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            raise
    
    def load_data_from_csv(self, csv_path: str = None) -> pd.DataFrame:
        """
        Load SHRI data dari CSV file (real data dari ekstraksi Excel)
        
        Args:
            csv_path: Path to CSV file. If None, uses default path.
            
        Returns:
            pd.DataFrame: Data sensus harian dengan kolom tanggal dan BOR
        """
        try:
            # Use default CSV path if not provided
            if csv_path is None:
                csv_path = os.path.join(
                    os.path.dirname(os.path.dirname(self.model_dir)),
                    'data',
                    'shri_training_data.csv'
                )
            
            if not os.path.exists(csv_path):
                raise FileNotFoundError(f"CSV file not found: {csv_path}")
            
            # Load CSV
            df = pd.read_csv(csv_path)
            
            # Convert date column
            df['tanggal'] = pd.to_datetime(df['tanggal'])
            df.set_index('tanggal', inplace=True)
            df = df[['bor']]  # Keep only BOR column
            
            # Validate data
            if len(df) < self.config['data']['min_data_points']:
                raise ValueError(f"Insufficient data points: {len(df)} < {self.config['data']['min_data_points']}")
            
            # Store data
            self.data = df
            
            logger.info(f"Data loaded successfully from CSV")
            logger.info(f"CSV path: {csv_path}")
            logger.info(f"Total data points: {len(df)}")
            logger.info(f"Date range: {df.index.min()} to {df.index.max()}")
            logger.info(f"BOR range: {df['bor'].min():.1f}% to {df['bor'].max():.1f}%")
            logger.info(f"BOR mean: {df['bor'].mean():.1f}%")
            
            return df
            
        except Exception as e:
            logger.error(f"Error loading data from CSV: {e}")
            raise
    
    def load_data_from_database(self) -> pd.DataFrame:
        """
        Load SHRI data dari database SQLite
        
        Returns:
            pd.DataFrame: Data sensus harian dengan kolom tanggal dan BOR
        """
        try:
            # Database path configuration
            db_config = self.config['database']
            db_path = os.path.join(self.model_dir, db_config['path'])
            
            if not os.path.exists(db_path):
                raise FileNotFoundError(f"Database file not found: {db_path}")
            
            # Connect to database
            conn = sqlite3.connect(db_path)
            
            # Query data
            query = f"""
            SELECT {db_config['date_column']}, {db_config['target_column']}
            FROM {db_config['table']}
            WHERE {db_config['target_column']} IS NOT NULL
            ORDER BY {db_config['date_column']}
            """
            
            # Load data
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            # Convert date column
            df[db_config['date_column']] = pd.to_datetime(df[db_config['date_column']])
            df.set_index(db_config['date_column'], inplace=True)
            
            # Validate data
            if len(df) < self.config['data']['min_data_points']:
                raise ValueError(f"Insufficient data points: {len(df)} < {self.config['data']['min_data_points']}")
            
            # Store data
            self.data = df
            
            logger.info(f"Data loaded successfully from database")
            logger.info(f"Total data points: {len(df)}")
            logger.info(f"Date range: {df.index.min()} to {df.index.max()}")
            logger.info(f"Target variable: {db_config['target_column']}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error loading data from database: {e}")
            raise
    
    def preprocess_data(self) -> Tuple[pd.Series, pd.Series]:
        """
        Preprocess data dan split train/test
        
        Returns:
            Tuple[pd.Series, pd.Series]: train_data, test_data
        """
        try:
            if self.data is None:
                raise ValueError("Data not loaded. Call load_data_from_csv() or load_data_from_database() first.")
            
            # Get target series - handle both 'bor' and configured target column
            if 'bor' in self.data.columns:
                series = self.data['bor'].copy()
            else:
                target_col = self.config['database']['target_column']
                series = self.data[target_col].copy()
            
            # Handle missing values
            if self.config['data']['missing_value_strategy'] == 'forward_fill':
                series = series.fillna(method='ffill').fillna(method='bfill')
            
            # Remove outliers using IQR method
            if self.config['data']['outlier_method'] == 'iqr':
                Q1 = series.quantile(0.25)
                Q3 = series.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                # Count outliers
                outliers = ((series < lower_bound) | (series > upper_bound)).sum()
                if outliers > 0:
                    logger.info(f"Outliers detected and handled: {outliers} points")
                
                # Replace outliers with median
                median_value = series.median()
                series = series.where(
                    (series >= lower_bound) & (series <= upper_bound), 
                    median_value
                )
            
            # Train/test split
            split_ratio = self.config['data']['train_test_split']
            split_index = int(len(series) * split_ratio)
            
            train_data = series.iloc[:split_index]
            test_data = series.iloc[split_index:]
            
            self.train_data = train_data
            self.test_data = test_data
            
            logger.info(f"Data preprocessing completed")
            logger.info(f"Training data: {len(train_data)} points ({train_data.index.min()} to {train_data.index.max()})")
            logger.info(f"Testing data: {len(test_data)} points ({test_data.index.min()} to {test_data.index.max()})")
            
            return train_data, test_data
            
        except Exception as e:
            logger.error(f"Error preprocessing data: {e}")
            raise
    
    def check_stationarity(self, data: pd.Series) -> Dict[str, Any]:
        """
        Uji stasioneritas menggunakan Augmented Dickey-Fuller Test
        
        Args:
            data: Time series data
            
        Returns:
            Dict: Hasil uji stasioneritas
        """
        try:
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
            
            logger.info(f"ADF Stationarity Test Results:")
            logger.info(f"  ADF Statistic: {adf_result['adf_statistic']:.6f}")
            logger.info(f"  p-value: {adf_result['p_value']:.6f}")
            logger.info(f"  Conclusion: {adf_result['conclusion']}")
            
            return adf_result
            
        except Exception as e:
            logger.error(f"Error in stationarity test: {e}")
            raise
    
    def grid_search_sarima(self) -> Dict[str, Any]:
        """
        Grid search untuk parameter SARIMA terbaik
        
        Returns:
            Dict: Best parameters dan hasil grid search
        """
        try:
            if self.train_data is None:
                raise ValueError("Training data not available. Call preprocess_data() first.")
            
            logger.info("Starting SARIMA Grid Search...")
            
            # Get parameter ranges from config
            sarima_config = self.config['sarima']
            p_range = sarima_config['p_range']
            d_range = sarima_config['d_range']
            q_range = sarima_config['q_range']
            P_range = sarima_config['P_range']
            D_range = sarima_config['D_range']
            Q_range = sarima_config['Q_range']
            seasonal_periods = sarima_config['seasonal_periods']
            
            best_aic = float('inf')
            best_params = None
            search_results = []
            total_combinations = len(p_range) * len(d_range) * len(q_range) * len(P_range) * len(D_range) * len(Q_range) * len(seasonal_periods)
            
            logger.info(f"Testing {total_combinations} parameter combinations...")
            
            combination_count = 0
            
            for s in seasonal_periods:
                for p in p_range:
                    for d in d_range:
                        for q in q_range:
                            for P in P_range:
                                for D in D_range:
                                    for Q in Q_range:
                                        combination_count += 1
                                        
                                        try:
                                            # Create and fit model
                                            model = SARIMAX(
                                                self.train_data,
                                                order=(p, d, q),
                                                seasonal_order=(P, D, Q, s),
                                                enforce_stationarity=sarima_config['enforce_stationarity'],
                                                enforce_invertibility=sarima_config['enforce_invertibility']
                                            )
                                            
                                            fitted_model = model.fit(
                                                disp=False,
                                                method=sarima_config['method'],
                                                maxiter=sarima_config['maxiter']
                                            )
                                            
                                            # Get AIC/BIC metrics
                                            aic = fitted_model.aic
                                            bic = fitted_model.bic
                                            
                                            # Calculate MAE on test set for better evaluation
                                            try:
                                                test_predictions = fitted_model.forecast(steps=len(self.test_data))
                                                mae = mean_absolute_error(self.test_data, test_predictions)
                                            except:
                                                mae = float('inf')
                                            
                                            # Store result
                                            result = {
                                                'order': (p, d, q),
                                                'seasonal_order': (P, D, Q, s),
                                                'aic': aic,
                                                'bic': bic,
                                                'mae': mae,
                                                'converged': fitted_model.mle_retvals['converged']
                                            }
                                            search_results.append(result)
                                            
                                            # Check if this is the best model (by AIC, but track MAE too)
                                            if aic < best_aic and fitted_model.mle_retvals['converged']:
                                                best_aic = aic
                                                best_params = result.copy()
                                            
                                            # Progress logging (every 10% of combinations)
                                            if combination_count % max(1, total_combinations // 10) == 0:
                                                progress = (combination_count / total_combinations) * 100
                                                logger.info(f"Grid search progress: {progress:.1f}% - Current best AIC: {best_aic:.2f}")
                                        
                                        except Exception as model_error:
                                            # Skip this combination if model fails
                                            continue
            
            if best_params is None:
                raise ValueError("No valid SARIMA model found in grid search")
            
            self.best_params = best_params
            
            # Sort results by AIC (primary) and MAE (secondary)
            search_results.sort(key=lambda x: (x['aic'], x.get('mae', float('inf'))))
            
            logger.info("Grid Search Completed!")
            logger.info(f"Best model: SARIMA{best_params['order']}x{best_params['seasonal_order']}")
            logger.info(f"Best AIC: {best_params['aic']:.4f}")
            logger.info(f"Best BIC: {best_params['bic']:.4f}")
            if 'mae' in best_params and best_params['mae'] != float('inf'):
                logger.info(f"Best MAE: {best_params['mae']:.4f} (on test set)")
            
            # Log top 5 models
            logger.info(f"\nTop 5 Models by AIC:")
            for i, result in enumerate(search_results[:5], 1):
                mae_str = f", MAE: {result['mae']:.4f}" if result.get('mae') != float('inf') else ""
                logger.info(f"  {i}. SARIMA{result['order']}x{result['seasonal_order']} - AIC: {result['aic']:.2f}{mae_str}")
            
            return {
                'best_params': best_params,
                'search_results': search_results[:20],  # Top 20 models
                'total_models_tested': len(search_results)
            }
            
        except Exception as e:
            logger.error(f"Error in grid search: {e}")
            raise
    
    def train_final_model(self) -> Any:
        """
        Train final model dengan parameter terbaik
        
        Returns:
            Fitted SARIMA model
        """
        try:
            if self.best_params is None:
                raise ValueError("Best parameters not found. Run grid_search_sarima() first.")
            
            logger.info("Training final SARIMA model...")
            
            # Create final model
            final_model = SARIMAX(
                self.train_data,
                order=self.best_params['order'],
                seasonal_order=self.best_params['seasonal_order'],
                enforce_stationarity=self.config['sarima']['enforce_stationarity'],
                enforce_invertibility=self.config['sarima']['enforce_invertibility']
            )
            
            # Fit model
            self.best_model = final_model.fit(
                disp=False,
                method=self.config['sarima']['method'],
                maxiter=self.config['sarima']['maxiter']
            )
            
            # Model diagnostics
            residuals = self.best_model.resid
            
            # Ljung-Box test for residual autocorrelation
            ljung_box = acorr_ljungbox(residuals, lags=10, return_df=True)
            white_noise = all(ljung_box['lb_pvalue'] > self.config['model_selection']['ljung_box_alpha'])
            
            model_info = {
                'order': self.best_params['order'],
                'seasonal_order': self.best_params['seasonal_order'],
                'aic': float(self.best_model.aic),
                'bic': float(self.best_model.bic),
                'log_likelihood': float(self.best_model.llf),
                'converged': self.best_model.mle_retvals['converged'],
                'residuals_white_noise': white_noise,
                'ljung_box_p_values': ljung_box['lb_pvalue'].tolist()
            }
            
            logger.info("Final model training completed!")
            logger.info(f"Model: SARIMA{model_info['order']}x{model_info['seasonal_order']}")
            logger.info(f"AIC: {model_info['aic']:.4f}")
            logger.info(f"BIC: {model_info['bic']:.4f}")
            logger.info(f"Residuals white noise test: {'✓ PASSED' if white_noise else '✗ FAILED'}")
            
            return self.best_model
            
        except Exception as e:
            logger.error(f"Error training final model: {e}")
            raise
    
    def evaluate_model(self) -> Dict[str, float]:
        """
        Evaluasi model pada test set
        
        Returns:
            Dict: Performance metrics (RMSE, MAE, MAPE)
        """
        try:
            if self.best_model is None:
                raise ValueError("Model not trained. Call train_final_model() first.")
            
            logger.info("Evaluating model performance on test set...")
            
            # Generate predictions for test period
            forecast_steps = len(self.test_data)
            forecast_result = self.best_model.get_forecast(steps=forecast_steps)
            predictions = forecast_result.predicted_mean
            
            # Align predictions with test data
            actual = self.test_data.values
            predicted = predictions.values
            
            # Calculate metrics
            rmse = np.sqrt(mean_squared_error(actual, predicted))
            mae = mean_absolute_error(actual, predicted)
            
            # MAPE calculation with zero-handling
            mape_values = []
            for i in range(len(actual)):
                if actual[i] != 0:
                    mape_values.append(abs((actual[i] - predicted[i]) / actual[i]))
            mape = np.mean(mape_values) * 100 if mape_values else 0
            
            # Additional metrics
            mse = mean_squared_error(actual, predicted)
            
            # R-squared
            ss_res = np.sum((actual - predicted) ** 2)
            ss_tot = np.sum((actual - np.mean(actual)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            
            metrics = {
                'rmse': float(rmse),
                'mae': float(mae),
                'mape': float(mape),
                'mse': float(mse),
                'r_squared': float(r_squared),
                'n_test_points': len(actual)
            }
            
            self.performance_metrics = metrics
            
            # Performance evaluation against targets
            target_mape = self.config['performance']['target_mape']
            target_rmse = self.config['performance']['target_rmse']
            target_mae = self.config['performance']['target_mae']
            
            # Context for RSJ data
            data_mean = np.mean(actual)
            relative_mae = (mae / data_mean) * 100 if data_mean > 0 else 0
            
            logger.info("Model Performance Evaluation:")
            logger.info(f"  MAE: {metrics['mae']:.4f} (Target: < {target_mae}) ⭐ PRIMARY METRIC")
            logger.info(f"  RMSE: {metrics['rmse']:.4f} (Target: < {target_rmse})")
            logger.info(f"  MAPE: {metrics['mape']:.2f}% (Target: < {target_mape}%)")
            logger.info(f"  R²: {metrics['r_squared']:.4f}")
            logger.info(f"\n  📊 RSJ Context:")
            logger.info(f"     Actual BOR (test): {data_mean:.2f}%")
            logger.info(f"     Predicted BOR (test): {np.mean(predicted):.2f}%")
            logger.info(f"     Relative MAE: {relative_mae:.1f}% (MAE/mean)")
            logger.info(f"     Interpretation: ±{mae:.2f}% average error")
            
            # Check performance criteria
            criteria_met = {
                'mae_ok': metrics['mae'] < target_mae,
                'rmse_ok': metrics['rmse'] < target_rmse,
                'mape_ok': metrics['mape'] < target_mape
            }
            
            all_criteria_met = all(criteria_met.values())
            
            if all_criteria_met:
                logger.info("\n✓ Model meets ALL performance criteria for journal publication!")
            else:
                logger.warning("\n⚠ Model does not meet some performance criteria:")
                for criteria, met in criteria_met.items():
                    if not met:
                        logger.warning(f"  ✗ {criteria}")
                
                # Special note for RSJ data
                if criteria_met['mae_ok']:
                    logger.info("\n💡 NOTE: MAE criteria met - acceptable for RSJ data with low BOR")
                    logger.info("   MAPE is inflated due to low baseline values (RSJ characteristic)")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error evaluating model: {e}")
            raise
    
    def save_model(self) -> str:
        """
        Save trained model sebagai .pkl file
        
        Returns:
            str: Path to saved model file
        """
        try:
            if self.best_model is None:
                raise ValueError("No model to save. Train model first.")
            
            model_path = os.path.join(self.model_dir, self.config['output']['model_file'])
            
            # Save model
            with open(model_path, 'wb') as f:
                pickle.dump(self.best_model, f)
            
            logger.info(f"Model saved successfully: {model_path}")
            return model_path
            
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            raise
    
    def save_training_log(self) -> str:
        """
        Save training log dan metrics ke JSON file
        
        Returns:
            str: Path to saved log file
        """
        try:
            log_path = os.path.join(self.model_dir, self.config['output']['log_file'])
            
            # Prepare log data
            log_data = {
                'training_timestamp': datetime.now().isoformat(),
                'model_info': {
                    'order': self.best_params['order'] if self.best_params else None,
                    'seasonal_order': self.best_params['seasonal_order'] if self.best_params else None,
                    'model_formula': f"SARIMA{self.best_params['order']}x{self.best_params['seasonal_order']}" if self.best_params else None
                },
                'data_info': {
                    'total_data_points': len(self.data) if self.data is not None else 0,
                    'training_points': len(self.train_data) if self.train_data is not None else 0,
                    'testing_points': len(self.test_data) if self.test_data is not None else 0,
                    'date_range': {
                        'start': self.data.index.min().isoformat() if self.data is not None else None,
                        'end': self.data.index.max().isoformat() if self.data is not None else None
                    }
                },
                'model_performance': self.performance_metrics,
                'model_statistics': {
                    'aic': float(self.best_model.aic) if self.best_model else None,
                    'bic': float(self.best_model.bic) if self.best_model else None,
                    'log_likelihood': float(self.best_model.llf) if self.best_model else None,
                    'converged': self.best_model.mle_retvals['converged'] if self.best_model else None
                },
                'configuration': self.config
            }
            
            # Save log
            with open(log_path, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Training log saved: {log_path}")
            return log_path
            
        except Exception as e:
            logger.error(f"Error saving training log: {e}")
            raise
    
    def print_training_results(self):
        """
        Print final training results untuk jurnal
        """
        try:
            print("\n" + "="*80)
            print("HASIL TRAINING SARIMA MODEL")
            print("Penelitian: Peramalan Indikator Rumah Sakit Berbasis Sensus Harian Rawat Inap")
            print("="*80)
            
            if self.best_params and self.performance_metrics:
                # Model information
                order = self.best_params['order']
                seasonal_order = self.best_params['seasonal_order']
                
                print(f"\n📊 PARAMETER MODEL FINAL:")
                print(f"   Model: SARIMA{order}x{seasonal_order}")
                print(f"   Formula: SARIMA({order[0]},{order[1]},{order[2]})({seasonal_order[0]},{seasonal_order[1]},{seasonal_order[2]})_{seasonal_order[3]}")
                
                # Model statistics
                if self.best_model:
                    print(f"\n📈 STATISTIK MODEL:")
                    print(f"   AIC: {self.best_model.aic:.4f}")
                    print(f"   BIC: {self.best_model.bic:.4f}")
                    print(f"   Log-Likelihood: {self.best_model.llf:.4f}")
                    print(f"   Converged: {'✓ Yes' if self.best_model.mle_retvals['converged'] else '✗ No'}")
                
                # Performance metrics
                metrics = self.performance_metrics
                print(f"\n🎯 METRIK PERFORMA (Test Set):")
                print(f"   MAE: {metrics['mae']:.4f} ⭐ (PRIMARY METRIC untuk RSJ)")
                print(f"   RMSE: {metrics['rmse']:.4f}")
                print(f"   MAPE: {metrics['mape']:.2f}%")
                print(f"   R²: {metrics['r_squared']:.4f}")
                print(f"   Test Data Points: {metrics['n_test_points']}")
                
                # Data information
                if self.data is not None:
                    bor_col = 'bor' if 'bor' in self.data.columns else self.config['database']['target_column']
                    print(f"\n📅 INFORMASI DATA (RSJ Context):")
                    print(f"   Hospital Type: Rumah Sakit Jiwa (Psychiatric Hospital)")
                    print(f"   Total Data: {len(self.data)} hari")
                    print(f"   Training: {len(self.train_data)} hari")
                    print(f"   Testing: {len(self.test_data)} hari")
                    print(f"   Periode: {self.data.index.min().strftime('%Y-%m-%d')} s/d {self.data.index.max().strftime('%Y-%m-%d')}")
                    print(f"   BOR Mean: {self.data[bor_col].mean():.2f}% (Typical for RSJ: 15-30%)")
                    print(f"   BOR Range: {self.data[bor_col].min():.1f}% - {self.data[bor_col].max():.1f}%")
                
                # Performance criteria check
                target_mape = self.config['performance']['target_mape']
                target_rmse = self.config['performance']['target_rmse']
                target_mae = self.config['performance']['target_mae']
                
                print(f"\n✅ EVALUASI KRITERIA (Adjusted for RSJ):")
                print(f"   MAE < {target_mae}: {'✓ PASSED' if metrics['mae'] < target_mae else '✗ FAILED'} ({metrics['mae']:.4f}) ⭐ PRIMARY")
                print(f"   RMSE < {target_rmse}: {'✓ PASSED' if metrics['rmse'] < target_rmse else '✗ FAILED'} ({metrics['rmse']:.4f})")
                print(f"   MAPE < {target_mape}%: {'✓ PASSED' if metrics['mape'] < target_mape else '✗ FAILED'} ({metrics['mape']:.2f}%)")
                
                # Interpretation
                if metrics['mae'] < target_mae:
                    print(f"\n   💡 Model acceptable for RSJ data (MAE criteria met)")
                    print(f"      Average prediction error: ±{metrics['mae']:.2f}%")
                
                # Files generated
                print(f"\n📁 FILE OUTPUT:")
                print(f"   Model: {os.path.join(self.model_dir, self.config['output']['model_file'])}")
                print(f"   Log: {os.path.join(self.model_dir, self.config['output']['log_file'])}")
                
                # Research notes
                print(f"\n📝 STATEMENT UNTUK JURNAL:")
                print(f'   "Model SARIMA({order[0]},{order[1]},{order[2]})({seasonal_order[0]},{seasonal_order[1]},{seasonal_order[2]})_{seasonal_order[3]} dikembangkan')
                print(f'    untuk memprediksi BOR di RSJD dengan data {len(self.data)} hari observasi.')
                print(f'    Model mencapai MAE {metrics["mae"]:.2f}% dan MAPE {metrics["mape"]:.1f}% pada testing set.')
                print(f'    Data RSJ memiliki karakteristik BOR rendah (mean: {self.data[bor_col].mean():.1f}%)')
                print(f'    yang berbeda dari rumah sakit umum, sehingga MAE lebih appropriate')
                print(f'    sebagai metric evaluasi dibanding MAPE."')
                
            else:
                print("\n❌ TRAINING BELUM SELESAI")
                print("Jalankan full training pipeline untuk mendapatkan hasil.")
            
            print("\n" + "="*80)
            
        except Exception as e:
            logger.error(f"Error printing results: {e}")
    
    def run_full_pipeline(self, use_csv: bool = True):
        """
        Jalankan seluruh training pipeline
        
        Args:
            use_csv: If True, load real data from CSV. If False, load from database.
        """
        try:
            logger.info("🚀 STARTING SARIMA TRAINING PIPELINE")
            logger.info("="*60)
            
            # Step 1: Load data
            if use_csv:
                logger.info("Step 1: Loading REAL data from CSV (extracted from Excel)...")
                self.load_data_from_csv()
            else:
                logger.info("Step 1: Loading data from database...")
                self.load_data_from_database()
            
            # Step 2: Preprocess data
            logger.info("Step 2: Preprocessing data and train/test split...")
            self.preprocess_data()
            
            # Step 3: Check stationarity
            logger.info("Step 3: Checking data stationarity...")
            stationarity_result = self.check_stationarity(self.train_data)
            
            # Step 4: Grid search
            logger.info("Step 4: Grid search for optimal SARIMA parameters...")
            grid_search_results = self.grid_search_sarima()
            
            # Step 5: Train final model
            logger.info("Step 5: Training final model with best parameters...")
            self.train_final_model()
            
            # Step 6: Evaluate model
            logger.info("Step 6: Evaluating model performance...")
            self.evaluate_model()
            
            # Step 7: Save model and logs
            logger.info("Step 7: Saving model and training logs...")
            self.save_model()
            self.save_training_log()
            
            # Step 8: Print results
            logger.info("Step 8: Generating training results summary...")
            self.print_training_results()
            
            logger.info("🎉 TRAINING PIPELINE COMPLETED SUCCESSFULLY!")
            
        except Exception as e:
            logger.error(f"❌ TRAINING PIPELINE FAILED: {e}")
            raise


def main():
    """
    Main function untuk menjalankan SARIMA training
    """
    try:
        # Initialize trainer
        config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
        trainer = SARIMATrainer(config_path)
        
        # Run full training pipeline with REAL CSV data (default)
        # Use use_csv=False to load from database instead
        trainer.run_full_pipeline(use_csv=True)
        
    except Exception as e:
        logger.error(f"Training failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()