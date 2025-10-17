"""
Quick script: Train SARIMA s=7 dan buat comparison dengan s=30
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from statsmodels.tsa.statespace.sarimax import SARIMAX
import pickle

# Load data
data_path = Path(__file__).parent.parent.parent / "data" / "shri_training_data.csv"
df = pd.read_csv(data_path)
df['tanggal'] = pd.to_datetime(df['tanggal'])
df.set_index('tanggal', inplace=True)

# Split
train_size = int(len(df) * 0.8)
train = df.iloc[:train_size]['bor']
test = df.iloc[train_size:]['bor']

print(f"Training SARIMA s=7...")
print(f"Training: {len(train)}, Testing: {len(test)}")

# Train SARIMA s=7 dengan parameter terbaik (0,1,2)(1,1,2) seperti s=30
try:
    model_s7 = SARIMAX(train, 
                       order=(0, 1, 2),
                       seasonal_order=(1, 1, 2, 7),
                       enforce_stationarity=False,
                       enforce_invertibility=False)
    
    fitted_s7 = model_s7.fit(disp=False, maxiter=200, method='lbfgs')
    print(f"✅ SARIMA s=7 trained successfully")
    print(f"   AIC: {fitted_s7.aic:.2f}")
    
    # Save model
    model_path = Path(__file__).parent / "sarima_model_s7.pkl"
    with open(model_path, 'wb') as f:
        pickle.dump(fitted_s7, f)
    print(f"✅ Model saved: {model_path}")
    
    # Predict
    pred_s7 = fitted_s7.forecast(steps=len(test))
    
    # Calculate metrics
    actual = test.values
    
    # RMSE
    rmse_s7 = np.sqrt(np.mean((actual - pred_s7)**2))
    
    # MAE
    mae_s7 = np.mean(np.abs(actual - pred_s7))
    
    # MAPE
    mape_s7 = np.mean(np.abs((actual - pred_s7) / actual)) * 100
    
    # WAPE
    wape_s7 = (np.sum(np.abs(actual - pred_s7)) / np.sum(actual)) * 100
    
    print(f"\n📊 SARIMA s=7 Performance:")
    print(f"   RMSE: {rmse_s7:.2f}")
    print(f"   MAE: {mae_s7:.2f}")
    print(f"   MAPE: {mape_s7:.2f}%")
    print(f"   WAPE: {wape_s7:.2f}%")
    print(f"   AIC: {fitted_s7.aic:.2f}")
    
except Exception as e:
    print(f"❌ Error training s=7: {e}")
    raise

# Load SARIMA s=30 model
print(f"\nLoading SARIMA s=30...")
model_s30_path = Path(__file__).parent / "sarima_model.pkl"
with open(model_s30_path, 'rb') as f:
    fitted_s30 = pickle.load(f)

pred_s30 = fitted_s30.forecast(steps=len(test))

# Calculate s=30 metrics
rmse_s30 = np.sqrt(np.mean((actual - pred_s30)**2))
mae_s30 = np.mean(np.abs(actual - pred_s30))
mape_s30 = np.mean(np.abs((actual - pred_s30) / actual)) * 100
wape_s30 = (np.sum(np.abs(actual - pred_s30)) / np.sum(actual)) * 100

print(f"\n📊 SARIMA s=30 Performance:")
print(f"   RMSE: {rmse_s30:.2f}")
print(f"   MAE: {mae_s30:.2f}")
print(f"   MAPE: {mape_s30:.2f}%")
print(f"   WAPE: {wape_s30:.2f}%")
print(f"   AIC: {fitted_s30.aic:.2f}")

# Create comparison JSON
comparison = {
    "timestamp": pd.Timestamp.now().isoformat(),
    "data_info": {
        "total_points": len(df),
        "train_points": len(train),
        "test_points": len(test)
    },
    "sarima_s7": {
        "order": [0, 1, 2],
        "seasonal_order": [1, 1, 2, 7],
        "aic": float(fitted_s7.aic),
        "rmse": float(rmse_s7),
        "mae": float(mae_s7),
        "mape": float(mape_s7),
        "wape": float(wape_s7)
    },
    "sarima_s30": {
        "order": [0, 1, 2],
        "seasonal_order": [1, 1, 2, 30],
        "aic": float(fitted_s30.aic),
        "rmse": float(rmse_s30),
        "mae": float(mae_s30),
        "mape": float(mape_s30),
        "wape": float(wape_s30)
    },
    "winner": "s=30" if wape_s30 < wape_s7 else "s=7",
    "improvement": {
        "wape": float(wape_s7 - wape_s30),
        "aic": float(fitted_s7.aic - fitted_s30.aic),
        "mae": float(mae_s7 - mae_s30),
        "rmse": float(rmse_s7 - rmse_s30)
    }
}

# Save comparison
output_path = Path(__file__).parent / "comparison_s7_vs_s30_results.json"
with open(output_path, 'w') as f:
    json.dump(comparison, f, indent=2)

print(f"\n✅ Comparison saved: {output_path}")
print(f"\n🏆 WINNER: {comparison['winner']}")
print(f"   WAPE improvement: {comparison['improvement']['wape']:.2f}%")
print(f"   AIC improvement: {comparison['improvement']['aic']:.2f}")
