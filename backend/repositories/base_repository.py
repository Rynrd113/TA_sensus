# backend/repositories/base_repository.py
"""
Base Repository Class
Generic CRUD operations for all repositories
"""

from typing import TypeVar, Generic, Optional, List, Type, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

# Type variable for model type
ModelType = TypeVar("ModelType")

class BaseRepository(Generic[ModelType]):
    """Base repository class with common CRUD operations"""
    
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db
    
    def get_by_id(self, id: Any) -> Optional[ModelType]:
        """Get a single record by ID"""
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self, limit: int = 100, offset: int = 0) -> List[ModelType]:
        """Get all records with optional pagination"""
        return self.db.query(self.model).offset(offset).limit(limit).all()
    
    def create(self, obj_data: dict) -> ModelType:
        """Create a new record"""
        try:
            db_obj = self.model(**obj_data)
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            return db_obj
        except IntegrityError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Database integrity error: {str(e)}"
            )
    
    def update(self, id: Any, obj_data: dict) -> Optional[ModelType]:
        """Update an existing record"""
        db_obj = self.get_by_id(id)
        if db_obj:
            try:
                for field, value in obj_data.items():
                    if hasattr(db_obj, field):
                        setattr(db_obj, field, value)
                
                self.db.commit()
                self.db.refresh(db_obj)
                return db_obj
            except IntegrityError as e:
                self.db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Database integrity error: {str(e)}"
                )
        return None
    
    def delete(self, id: Any) -> bool:
        """Delete a record by ID"""
        db_obj = self.get_by_id(id)
        if db_obj:
            self.db.delete(db_obj)
            self.db.commit()
            return True
        return False
    
    def count(self) -> int:
        """Count total records"""
        return self.db.query(self.model).count()
    
    def exists(self, id: Any) -> bool:
        """Check if a record exists by ID"""
        return self.db.query(self.model).filter(self.model.id == id).first() is not None