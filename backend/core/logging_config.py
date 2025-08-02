# backend/core/logging_config.py
import logging
import os
from datetime import datetime

# Pastikan direktori logs ada
os.makedirs("logs", exist_ok=True)

# Konfigurasi logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("sensus-rs")

def log_sensus_activity(action: str, data: dict):
    """Log aktivitas sensus dengan format standar"""
    logger.info(f"SENSUS_ACTIVITY - {action}: {data}")

def log_error(action: str, error: str):
    """Log error dengan format standar"""
    logger.error(f"ERROR - {action}: {error}")

def log_prediction(days: int, results: list):
    """Log aktivitas prediksi"""
    logger.info(f"PREDICTION - Generated {days} days forecast: {len(results)} results")
