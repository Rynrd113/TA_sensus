# backend/database/engine.py
from sqlalchemy import create_engine
from core.config import settings
import os

# Pastikan direktori db ada
db_path = settings.DATABASE_URL.replace("sqlite:///", "")
os.makedirs(os.path.dirname(db_path), exist_ok=True)

# backend/database/engine.py
from sqlalchemy import create_engine
from core.config import settings
import os

# Pastikan direktori db ada
db_path = settings.DATABASE_URL.replace("sqlite:///", "")
os.makedirs(os.path.dirname(db_path), exist_ok=True)

engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False},  # Penting untuk SQLite
    echo=False
)