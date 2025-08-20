# backend/tasks/scheduler.py
import schedule
import time
import threading
from datetime import datetime
from ml.train import train_sarima_and_save
from core.logging_config import log_error

def retrain_model_weekly():
    """Retrain model SARIMA otomatis setiap minggu"""
    try:
        log_error("SCHEDULER", "Starting weekly SARIMA model retraining...")
        success = train_sarima_and_save()
        
        if success:
            log_error("SCHEDULER", "Weekly SARIMA model retraining completed successfully")
        else:
            log_error("SCHEDULER", "Weekly SARIMA model retraining failed - insufficient data")
    except Exception as e:
        log_error("SCHEDULER", f"Weekly SARIMA model retraining error: {str(e)}")

def start_scheduler():
    """Start background scheduler"""
    # Schedule retrain setiap Minggu jam 02:00
    schedule.every().sunday.at("02:00").do(retrain_model_weekly)
    
    log_error("SCHEDULER", "Scheduler started - Weekly SARIMA retrain scheduled for Sunday 02:00")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

def start_scheduler_thread():
    """Start scheduler in background thread"""
    scheduler_thread = threading.Thread(target=start_scheduler, daemon=True)
    scheduler_thread.start()
    log_error("SCHEDULER", "Background scheduler thread started")
