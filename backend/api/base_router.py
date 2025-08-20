# backend/api/base_router.py
"""
Base Router Class
Implementasi DRY untuk semua router di backend
Menerapkan prinsip inheritance dan reusable code
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Type, List, Optional, Dict, Any
from abc import ABC, abstractmethod

from database.session import get_db
from core.logging_config import log_error


class BaseRouter(ABC):
    """
    Abstract Base Router untuk standardisasi CRUD operations
    Menerapkan prinsip DRY dan Single Responsibility
    """
    
    def __init__(self, prefix: str, tags: List[str], model_class: Type):
        self.router = APIRouter(prefix=prefix, tags=tags)
        self.model_class = model_class
        self.prefix = prefix
        self._register_routes()
    
    @abstractmethod
    def get_response_model(self):
        """Return Pydantic response model"""
        pass
    
    @abstractmethod
    def get_create_model(self):
        """Return Pydantic create model"""
        pass
    
    def _register_routes(self):
        """Register standard CRUD routes"""
        # Override in subclass if needed
        pass
    
    def create_standard_get_all_route(
        self, 
        response_model: Type,
        func_name: str = "get_all",
        limit_default: int = 30
    ):
        """Create standard GET all route"""
        
        @self.router.get("/", response_model=List[response_model])
        def get_all_items(
            limit: int = limit_default,
            offset: int = 0,
            db: Session = Depends(get_db)
        ):
            try:
                items = db.query(self.model_class)\
                         .offset(offset)\
                         .limit(limit)\
                         .all()
                return items
            except Exception as e:
                log_error(f"{func_name.upper()}", f"Database error: {str(e)}")
                raise HTTPException(status_code=500, detail="Gagal mengambil data")
    
    def create_standard_get_by_id_route(
        self, 
        response_model: Type,
        func_name: str = "get_by_id"
    ):
        """Create standard GET by ID route"""
        
        @self.router.get("/{item_id}", response_model=response_model)
        def get_item_by_id(
            item_id: int,
            db: Session = Depends(get_db)
        ):
            try:
                item = db.query(self.model_class)\
                        .filter(self.model_class.id == item_id)\
                        .first()
                
                if not item:
                    raise HTTPException(status_code=404, detail="Data tidak ditemukan")
                
                return item
            except HTTPException:
                raise
            except Exception as e:
                log_error(f"{func_name.upper()}", f"Database error: {str(e)}")
                raise HTTPException(status_code=500, detail="Gagal mengambil data")
    
    def create_standard_delete_route(
        self,
        func_name: str = "delete"
    ):
        """Create standard DELETE route"""
        
        @self.router.delete("/{item_id}")
        def delete_item(
            item_id: int,
            db: Session = Depends(get_db)
        ):
            try:
                item = db.query(self.model_class)\
                        .filter(self.model_class.id == item_id)\
                        .first()
                
                if not item:
                    raise HTTPException(status_code=404, detail="Data tidak ditemukan")
                
                db.delete(item)
                db.commit()
                
                return {"message": "Data berhasil dihapus"}
            except HTTPException:
                raise
            except Exception as e:
                log_error(f"{func_name.upper()}", f"Database error: {str(e)}")
                db.rollback()
                raise HTTPException(status_code=500, detail="Gagal menghapus data")
    
    def add_custom_validation(self, validation_func):
        """Add custom validation to router"""
        self.custom_validation = validation_func
    
    def handle_database_error(self, operation: str, error: Exception, db: Session):
        """Centralized database error handling"""
        log_error(operation, f"Database error: {str(error)}")
        if db:
            db.rollback()
        raise HTTPException(status_code=500, detail=f"Gagal {operation.lower()}")


# Utility functions untuk common operations
def get_pagination_params(limit: int = 30, offset: int = 0) -> Dict[str, int]:
    """Standard pagination parameters"""
    return {
        "limit": min(limit, 100),  # Max 100 items
        "offset": max(offset, 0)   # Min 0 offset
    }

def build_query_filters(model_class: Type, filters: Dict[str, Any]):
    """Build SQLAlchemy filters from dict"""
    query_filters = []
    
    for key, value in filters.items():
        if hasattr(model_class, key) and value is not None:
            attr = getattr(model_class, key)
            query_filters.append(attr == value)
    
    return query_filters

def validate_date_range(start_date: str, end_date: str) -> bool:
    """Validate date range"""
    from datetime import datetime
    
    try:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        return start <= end
    except ValueError:
        return False
