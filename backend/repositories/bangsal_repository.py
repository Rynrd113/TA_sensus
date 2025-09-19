# backend/repositories/bangsal_repository.py
"""
Bangsal Repository
Database operations for bangsal (hospital ward) management
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, asc, func
from models.bangsal import Bangsal, KamarBangsal
from schemas.bangsal import BangsalCreate, BangsalUpdate, KamarBangsalCreate, KamarBangsalUpdate
from repositories.base_repository import BaseRepository

class BangsalRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db, Bangsal)

    # Core CRUD Operations
    def create_bangsal(self, bangsal_data: BangsalCreate, created_by: Optional[int] = None) -> Bangsal:
        """Create new bangsal"""
        bangsal_dict = bangsal_data.model_dump()
        if created_by:
            bangsal_dict['created_by'] = created_by
            bangsal_dict['updated_by'] = created_by
        
        bangsal = Bangsal(**bangsal_dict)
        self.db.add(bangsal)
        self.db.commit()
        self.db.refresh(bangsal)
        return bangsal

    def get_bangsal_by_id(self, bangsal_id: int, include_rooms: bool = False) -> Optional[Bangsal]:
        """Get bangsal by ID with optional room details"""
        query = self.db.query(Bangsal)
        
        if include_rooms:
            query = query.options(joinedload(Bangsal.kamar_list))
        
        return query.filter(Bangsal.id == bangsal_id).first()

    def get_bangsal_by_kode(self, kode_bangsal: str, include_rooms: bool = False) -> Optional[Bangsal]:
        """Get bangsal by unique code"""
        query = self.db.query(Bangsal)
        
        if include_rooms:
            query = query.options(joinedload(Bangsal.kamar_list))
        
        return query.filter(Bangsal.kode_bangsal == kode_bangsal).first()

    def get_all_bangsal(
        self, 
        skip: int = 0, 
        limit: int = 100,
        include_inactive: bool = False,
        include_rooms: bool = False
    ) -> List[Bangsal]:
        """Get all bangsal with pagination and filters"""
        query = self.db.query(Bangsal)
        
        if include_rooms:
            query = query.options(joinedload(Bangsal.kamar_list))
        
        if not include_inactive:
            query = query.filter(Bangsal.is_active == True)
        
        return query.order_by(Bangsal.nama_bangsal).offset(skip).limit(limit).all()

    def update_bangsal(
        self, 
        bangsal_id: int, 
        bangsal_data: BangsalUpdate, 
        updated_by: Optional[int] = None
    ) -> Optional[Bangsal]:
        """Update bangsal information"""
        bangsal = self.get_bangsal_by_id(bangsal_id)
        if not bangsal:
            return None
        
        update_dict = bangsal_data.model_dump(exclude_unset=True)
        if updated_by:
            update_dict['updated_by'] = updated_by
        
        for key, value in update_dict.items():
            setattr(bangsal, key, value)
        
        self.db.commit()
        self.db.refresh(bangsal)
        return bangsal

    def delete_bangsal(self, bangsal_id: int) -> bool:
        """Soft delete bangsal (set inactive)"""
        bangsal = self.get_bangsal_by_id(bangsal_id)
        if not bangsal:
            return False
        
        bangsal.is_active = False
        self.db.commit()
        return True

    def hard_delete_bangsal(self, bangsal_id: int) -> bool:
        """Hard delete bangsal (permanently remove)"""
        bangsal = self.get_bangsal_by_id(bangsal_id)
        if not bangsal:
            return False
        
        self.db.delete(bangsal)
        self.db.commit()
        return True

    # Advanced Query Operations
    def search_bangsal(
        self,
        search_term: str,
        skip: int = 0,
        limit: int = 100,
        include_inactive: bool = False
    ) -> List[Bangsal]:
        """Search bangsal by name, code, or department"""
        query = self.db.query(Bangsal)
        
        if not include_inactive:
            query = query.filter(Bangsal.is_active == True)
        
        # Search in multiple fields
        search_filter = or_(
            Bangsal.nama_bangsal.ilike(f"%{search_term}%"),
            Bangsal.kode_bangsal.ilike(f"%{search_term}%"),
            Bangsal.departemen.ilike(f"%{search_term}%")
        )
        
        query = query.filter(search_filter)
        return query.order_by(Bangsal.nama_bangsal).offset(skip).limit(limit).all()

    def filter_bangsal(
        self,
        filters: Dict[str, Any],
        skip: int = 0,
        limit: int = 100
    ) -> List[Bangsal]:
        """Filter bangsal by multiple criteria"""
        query = self.db.query(Bangsal)
        
        # Apply filters
        if 'jenis_bangsal' in filters and filters['jenis_bangsal']:
            query = query.filter(Bangsal.jenis_bangsal == filters['jenis_bangsal'])
        
        if 'departemen' in filters and filters['departemen']:
            query = query.filter(Bangsal.departemen == filters['departemen'])
        
        if 'is_active' in filters:
            query = query.filter(Bangsal.is_active == filters['is_active'])
        
        if 'is_emergency_ready' in filters:
            query = query.filter(Bangsal.is_emergency_ready == filters['is_emergency_ready'])
        
        if 'lantai' in filters and filters['lantai'] is not None:
            query = query.filter(Bangsal.lantai == filters['lantai'])
        
        if 'gedung' in filters and filters['gedung']:
            query = query.filter(Bangsal.gedung == filters['gedung'])
        
        if 'min_available_beds' in filters and filters['min_available_beds'] is not None:
            query = query.filter(Bangsal.tempat_tidur_tersedia >= filters['min_available_beds'])
        
        if 'max_occupancy_rate' in filters and filters['max_occupancy_rate'] is not None:
            # Calculate occupancy rate in query
            query = query.filter(
                (Bangsal.tempat_tidur_terisi * 100.0 / Bangsal.kapasitas_total) <= filters['max_occupancy_rate']
            ).filter(Bangsal.kapasitas_total > 0)
        
        return query.order_by(Bangsal.nama_bangsal).offset(skip).limit(limit).all()

    def get_bangsal_by_department(self, departemen: str) -> List[Bangsal]:
        """Get all bangsal in a specific department"""
        return (self.db.query(Bangsal)
                .filter(Bangsal.departemen == departemen)
                .filter(Bangsal.is_active == True)
                .order_by(Bangsal.nama_bangsal)
                .all())

    def get_emergency_ready_bangsal(self) -> List[Bangsal]:
        """Get all bangsal ready for emergency admissions"""
        return (self.db.query(Bangsal)
                .filter(Bangsal.is_emergency_ready == True)
                .filter(Bangsal.is_active == True)
                .filter(Bangsal.tempat_tidur_tersedia > 0)
                .order_by(desc(Bangsal.tempat_tidur_tersedia))
                .all())

    def get_available_bangsal(self, min_beds: int = 1) -> List[Bangsal]:
        """Get bangsal with available beds"""
        return (self.db.query(Bangsal)
                .filter(Bangsal.is_active == True)
                .filter(Bangsal.tempat_tidur_tersedia >= min_beds)
                .order_by(desc(Bangsal.tempat_tidur_tersedia))
                .all())

    # Capacity Management
    def update_bed_capacity(self, bangsal_id: int, tempat_tidur_terisi: int) -> Optional[Bangsal]:
        """Update bed occupancy for a bangsal"""
        bangsal = self.get_bangsal_by_id(bangsal_id)
        if not bangsal:
            return None
        
        # Validate capacity
        if tempat_tidur_terisi > bangsal.kapasitas_total:
            raise ValueError("Tempat tidur terisi tidak boleh melebihi kapasitas total")
        
        if tempat_tidur_terisi < 0:
            raise ValueError("Tempat tidur terisi tidak boleh negatif")
        
        bangsal.tempat_tidur_terisi = tempat_tidur_terisi
        bangsal.tempat_tidur_tersedia = bangsal.kapasitas_total - tempat_tidur_terisi
        
        self.db.commit()
        self.db.refresh(bangsal)
        return bangsal

    def bulk_update_capacity(self, capacity_updates: List[Dict[str, Any]]) -> List[Bangsal]:
        """Bulk update bed capacity for multiple bangsal"""
        updated_bangsal = []
        
        for update in capacity_updates:
            bangsal_id = update.get('bangsal_id')
            tempat_tidur_terisi = update.get('tempat_tidur_terisi')
            
            if bangsal_id and tempat_tidur_terisi is not None:
                bangsal = self.update_bed_capacity(bangsal_id, tempat_tidur_terisi)
                if bangsal:
                    updated_bangsal.append(bangsal)
        
        return updated_bangsal

    # Statistics and Analytics
    def get_occupancy_statistics(self) -> Dict[str, Any]:
        """Get overall occupancy statistics"""
        result = (self.db.query(
            func.count(Bangsal.id).label('total_bangsal'),
            func.sum(func.case((Bangsal.is_active == True, 1), else_=0)).label('active_bangsal'),
            func.sum(func.case((Bangsal.is_active == True, Bangsal.kapasitas_total), else_=0)).label('total_capacity'),
            func.sum(func.case((Bangsal.is_active == True, Bangsal.tempat_tidur_terisi), else_=0)).label('total_occupied'),
            func.sum(func.case((Bangsal.is_active == True, Bangsal.tempat_tidur_tersedia), else_=0)).label('total_available'),
            func.sum(func.case((Bangsal.is_emergency_ready == True, 1), else_=0)).label('emergency_ready_bangsal')
        ).first())
        
        total_capacity = result.total_capacity or 0
        total_occupied = result.total_occupied or 0
        occupancy_rate = (total_occupied / total_capacity * 100) if total_capacity > 0 else 0
        
        return {
            'total_bangsal': result.total_bangsal or 0,
            'active_bangsal': result.active_bangsal or 0,
            'total_capacity': total_capacity,
            'total_occupied': total_occupied,
            'total_available': result.total_available or 0,
            'overall_occupancy_rate': round(occupancy_rate, 2),
            'emergency_ready_bangsal': result.emergency_ready_bangsal or 0
        }

    def get_department_statistics(self) -> List[Dict[str, Any]]:
        """Get statistics by department"""
        results = (self.db.query(
            Bangsal.departemen,
            func.count(Bangsal.id).label('total_bangsal'),
            func.sum(Bangsal.kapasitas_total).label('total_capacity'),
            func.sum(Bangsal.tempat_tidur_terisi).label('total_occupied'),
            func.sum(Bangsal.tempat_tidur_tersedia).label('total_available')
        )
        .filter(Bangsal.is_active == True)
        .filter(Bangsal.departemen.isnot(None))
        .group_by(Bangsal.departemen)
        .all())
        
        stats = []
        for result in results:
            occupancy_rate = (result.total_occupied / result.total_capacity * 100) if result.total_capacity > 0 else 0
            stats.append({
                'departemen': result.departemen,
                'total_bangsal': result.total_bangsal,
                'total_capacity': result.total_capacity,
                'total_occupied': result.total_occupied,
                'total_available': result.total_available,
                'occupancy_rate': round(occupancy_rate, 2)
            })
        
        return stats

    def count_bangsal(self, filters: Dict[str, Any] = None) -> int:
        """Count bangsal with optional filters"""
        query = self.db.query(Bangsal)
        
        if filters:
            if 'is_active' in filters:
                query = query.filter(Bangsal.is_active == filters['is_active'])
            if 'jenis_bangsal' in filters:
                query = query.filter(Bangsal.jenis_bangsal == filters['jenis_bangsal'])
            if 'departemen' in filters:
                query = query.filter(Bangsal.departemen == filters['departemen'])
        
        return query.count()


class KamarBangsalRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db, KamarBangsal)

    def create_kamar(self, kamar_data: KamarBangsalCreate) -> KamarBangsal:
        """Create new kamar in bangsal"""
        kamar = KamarBangsal(**kamar_data.model_dump())
        self.db.add(kamar)
        self.db.commit()
        self.db.refresh(kamar)
        return kamar

    def get_kamar_by_bangsal(self, bangsal_id: int) -> List[KamarBangsal]:
        """Get all rooms in a bangsal"""
        return (self.db.query(KamarBangsal)
                .filter(KamarBangsal.bangsal_id == bangsal_id)
                .filter(KamarBangsal.is_active == True)
                .order_by(KamarBangsal.nomor_kamar)
                .all())

    def get_available_kamar(self, bangsal_id: int) -> List[KamarBangsal]:
        """Get available rooms in a bangsal"""
        return (self.db.query(KamarBangsal)
                .filter(KamarBangsal.bangsal_id == bangsal_id)
                .filter(KamarBangsal.is_active == True)
                .filter(KamarBangsal.is_maintenance == False)
                .filter(KamarBangsal.status_kebersihan == "Bersih")
                .filter(KamarBangsal.tempat_tidur_terisi < KamarBangsal.kapasitas_kamar)
                .order_by(desc(KamarBangsal.kapasitas_kamar - KamarBangsal.tempat_tidur_terisi))
                .all())

    def update_kamar(self, kamar_id: int, kamar_data: KamarBangsalUpdate) -> Optional[KamarBangsal]:
        """Update kamar information"""
        kamar = self.db.query(KamarBangsal).filter(KamarBangsal.id == kamar_id).first()
        if not kamar:
            return None
        
        update_dict = kamar_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(kamar, key, value)
        
        self.db.commit()
        self.db.refresh(kamar)
        return kamar