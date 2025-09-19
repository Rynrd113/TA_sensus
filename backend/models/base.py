# backend/models/base.py
"""
Base SQLAlchemy Model Configuration
Shared base class for all database models
"""

from sqlalchemy.ext.declarative import declarative_base

# Create the base class for all models
Base = declarative_base()