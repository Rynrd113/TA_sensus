# backend/services/bangsal_service.py
"""
Bangsal Service
Business logic for bangsal (hospital ward) management
"""

import json
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from repositories.bangsal_repository import BangsalRepository, KamarBangsalRepository
from schemas.bangsal import (
    BangsalCreate, BangsalUpdate, BangsalResponse, BangsalList, BangsalSummary,
    KamarBangsalCreate, KamarBangsalUpdate, KamarBangsalResponse,
    CapacityUpdate, OccupancyStats, BangsalFilter
)
from models.bangsal import Bangsal, KamarBangsal
from core.logging_config import logger

class BangsalService:
    def __init__(self, db: Session):
        self.db = db
        self.bangsal_repo = BangsalRepository(db)
        self.kamar_repo = KamarBangsalRepository(db)

    # Core CRUD Operations
    async def create_bangsal(self, bangsal_data: BangsalCreate, created_by: Optional[int] = None) -> BangsalResponse:
        """Create new bangsal with validation"""
        try:
            # Check if kode_bangsal already exists
            existing = self.bangsal_repo.get_bangsal_by_kode(bangsal_data.kode_bangsal)
            if existing:
                raise ValueError(f"Kode bangsal '{bangsal_data.kode_bangsal}' sudah ada")
            
            # Validate facilities JSON if provided
            if bangsal_data.fasilitas:
                try:
                    json.loads(bangsal_data.fasilitas)
                except json.JSONDecodeError:
                    raise ValueError("Format fasilitas tidak valid (harus JSON)")
            
            # Calculate initial bed availability
            bangsal_dict = bangsal_data.model_dump()
            bangsal_dict['tempat_tidur_tersedia'] = bangsal_dict['kapasitas_total']
            bangsal_dict['tempat_tidur_terisi'] = 0
            
            # Create bangsal
            bangsal_create = BangsalCreate(**bangsal_dict)
            bangsal = self.bangsal_repo.create_bangsal(bangsal_create, created_by)
            
            logger.info(f"Bangsal created: {bangsal.kode_bangsal} by user {created_by}")
            
            # Convert to response schema
            response_data = bangsal.to_dict()
            response_data['occupancy_rate'] = bangsal.occupancy_rate
            response_data['available_beds'] = bangsal.available_beds
            
            return BangsalResponse(**response_data)
            
        except Exception as e:
            logger.error(f"Error creating bangsal: {str(e)}")
            raise

    async def get_bangsal(self, bangsal_id: int, include_rooms: bool = False) -> Optional[BangsalResponse]:
        """Get bangsal by ID"""
        try:
            bangsal = self.bangsal_repo.get_bangsal_by_id(bangsal_id, include_rooms)
            if not bangsal:
                return None
            
            response_data = bangsal.to_dict()
            response_data['occupancy_rate'] = bangsal.occupancy_rate
            response_data['available_beds'] = bangsal.available_beds
            
            return BangsalResponse(**response_data)
            
        except Exception as e:
            logger.error(f"Error getting bangsal {bangsal_id}: {str(e)}")
            raise

    async def get_bangsal_by_kode(self, kode_bangsal: str) -> Optional[BangsalResponse]:
        """Get bangsal by unique code"""
        try:
            bangsal = self.bangsal_repo.get_bangsal_by_kode(kode_bangsal)
            if not bangsal:
                return None
            
            response_data = bangsal.to_dict()
            response_data['occupancy_rate'] = bangsal.occupancy_rate
            response_data['available_beds'] = bangsal.available_beds
            
            return BangsalResponse(**response_data)
            
        except Exception as e:
            logger.error(f"Error getting bangsal by kode {kode_bangsal}: {str(e)}")
            raise

    async def get_bangsal_list(
        self, 
        page: int = 1, 
        per_page: int = 20,
        include_inactive: bool = False,
        search: Optional[str] = None,
        filters: Optional[BangsalFilter] = None
    ) -> BangsalList:
        """Get paginated list of bangsal"""
        try:
            skip = (page - 1) * per_page
            
            if search:
                bangsal_list = self.bangsal_repo.search_bangsal(
                    search, skip=skip, limit=per_page, include_inactive=include_inactive
                )
                total = len(self.bangsal_repo.search_bangsal(search, skip=0, limit=1000, include_inactive=include_inactive))
            elif filters:
                filter_dict = filters.model_dump(exclude_unset=True)
                bangsal_list = self.bangsal_repo.filter_bangsal(filter_dict, skip=skip, limit=per_page)
                total = len(self.bangsal_repo.filter_bangsal(filter_dict, skip=0, limit=1000))
            else:
                bangsal_list = self.bangsal_repo.get_all_bangsal(
                    skip=skip, limit=per_page, include_inactive=include_inactive
                )
                total = self.bangsal_repo.count_bangsal({'is_active': True} if not include_inactive else {})
            
            # Convert to response format
            bangsal_responses = []
            for bangsal in bangsal_list:
                response_data = bangsal.to_dict()
                response_data['occupancy_rate'] = bangsal.occupancy_rate
                response_data['available_beds'] = bangsal.available_beds
                bangsal_responses.append(BangsalResponse(**response_data))
            
            pages = (total + per_page - 1) // per_page
            
            return BangsalList(
                total=total,
                page=page,
                per_page=per_page,
                pages=pages,
                bangsal=bangsal_responses
            )
            
        except Exception as e:
            logger.error(f"Error getting bangsal list: {str(e)}")
            raise

    async def update_bangsal(
        self, 
        bangsal_id: int, 
        bangsal_data: BangsalUpdate, 
        updated_by: Optional[int] = None
    ) -> Optional[BangsalResponse]:
        """Update bangsal information"""
        try:
            # Check if bangsal exists
            existing = self.bangsal_repo.get_bangsal_by_id(bangsal_id)
            if not existing:
                return None
            
            # Check kode_bangsal uniqueness if updating
            if bangsal_data.kode_bangsal and bangsal_data.kode_bangsal != existing.kode_bangsal:
                kode_exists = self.bangsal_repo.get_bangsal_by_kode(bangsal_data.kode_bangsal)
                if kode_exists:
                    raise ValueError(f"Kode bangsal '{bangsal_data.kode_bangsal}' sudah ada")
            
            # Validate facilities JSON if provided
            if bangsal_data.fasilitas:
                try:
                    json.loads(bangsal_data.fasilitas)
                except json.JSONDecodeError:
                    raise ValueError("Format fasilitas tidak valid (harus JSON)")
            
            # Validate capacity updates
            if bangsal_data.tempat_tidur_terisi is not None:
                capacity = bangsal_data.kapasitas_total if bangsal_data.kapasitas_total is not None else existing.kapasitas_total
                if bangsal_data.tempat_tidur_terisi > capacity:
                    raise ValueError("Tempat tidur terisi tidak boleh melebihi kapasitas total")
            
            # Calculate available beds if capacity is updated
            if bangsal_data.kapasitas_total is not None or bangsal_data.tempat_tidur_terisi is not None:
                capacity = bangsal_data.kapasitas_total if bangsal_data.kapasitas_total is not None else existing.kapasitas_total
                terisi = bangsal_data.tempat_tidur_terisi if bangsal_data.tempat_tidur_terisi is not None else existing.tempat_tidur_terisi
                bangsal_data.tempat_tidur_tersedia = capacity - terisi
            
            # Update bangsal
            bangsal = self.bangsal_repo.update_bangsal(bangsal_id, bangsal_data, updated_by)
            if not bangsal:
                return None
            
            logger.info(f"Bangsal updated: {bangsal.kode_bangsal} by user {updated_by}")
            
            # Convert to response schema
            response_data = bangsal.to_dict()
            response_data['occupancy_rate'] = bangsal.occupancy_rate
            response_data['available_beds'] = bangsal.available_beds
            
            return BangsalResponse(**response_data)
            
        except Exception as e:
            logger.error(f"Error updating bangsal {bangsal_id}: {str(e)}")
            raise

    async def delete_bangsal(self, bangsal_id: int, hard_delete: bool = False) -> bool:
        """Delete bangsal (soft or hard delete)"""
        try:
            if hard_delete:
                success = self.bangsal_repo.hard_delete_bangsal(bangsal_id)
            else:
                success = self.bangsal_repo.delete_bangsal(bangsal_id)
            
            if success:
                logger.info(f"Bangsal {'hard' if hard_delete else 'soft'} deleted: ID {bangsal_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting bangsal {bangsal_id}: {str(e)}")
            raise

    # Capacity Management
    async def update_bed_capacity(self, bangsal_id: int, capacity_data: CapacityUpdate) -> Optional[BangsalResponse]:
        """Update bed capacity/occupancy"""
        try:
            bangsal = self.bangsal_repo.update_bed_capacity(bangsal_id, capacity_data.tempat_tidur_terisi)
            if not bangsal:
                return None
            
            logger.info(f"Bed capacity updated for bangsal {bangsal.kode_bangsal}: {capacity_data.tempat_tidur_terisi}")
            
            # Update room capacities if needed
            await self._sync_room_capacities(bangsal_id)
            
            response_data = bangsal.to_dict()
            response_data['occupancy_rate'] = bangsal.occupancy_rate
            response_data['available_beds'] = bangsal.available_beds
            
            return BangsalResponse(**response_data)
            
        except Exception as e:
            logger.error(f"Error updating bed capacity for bangsal {bangsal_id}: {str(e)}")
            raise

    async def bulk_update_capacity(self, capacity_updates: List[Dict[str, Any]]) -> List[BangsalResponse]:
        """Bulk update bed capacity for multiple bangsal"""
        try:
            updated_bangsal = self.bangsal_repo.bulk_update_capacity(capacity_updates)
            
            # Convert to response format
            responses = []
            for bangsal in updated_bangsal:
                response_data = bangsal.to_dict()
                response_data['occupancy_rate'] = bangsal.occupancy_rate
                response_data['available_beds'] = bangsal.available_beds
                responses.append(BangsalResponse(**response_data))
            
            logger.info(f"Bulk capacity update completed for {len(responses)} bangsal")
            return responses
            
        except Exception as e:
            logger.error(f"Error in bulk capacity update: {str(e)}")
            raise

    # Specialized Queries
    async def get_emergency_ready_bangsal(self) -> List[BangsalSummary]:
        """Get bangsal ready for emergency admissions"""
        try:
            bangsal_list = self.bangsal_repo.get_emergency_ready_bangsal()
            
            summaries = []
            for bangsal in bangsal_list:
                summaries.append(BangsalSummary(
                    id=bangsal.id,
                    nama_bangsal=bangsal.nama_bangsal,
                    kode_bangsal=bangsal.kode_bangsal,
                    kapasitas_total=bangsal.kapasitas_total,
                    tempat_tidur_tersedia=bangsal.tempat_tidur_tersedia,
                    tempat_tidur_terisi=bangsal.tempat_tidur_terisi,
                    occupancy_rate=bangsal.occupancy_rate,
                    jenis_bangsal=bangsal.jenis_bangsal,
                    is_active=bangsal.is_active,
                    is_emergency_ready=bangsal.is_emergency_ready
                ))
            
            return summaries
            
        except Exception as e:
            logger.error(f"Error getting emergency ready bangsal: {str(e)}")
            raise

    async def get_available_bangsal(self, min_beds: int = 1) -> List[BangsalSummary]:
        """Get bangsal with available beds"""
        try:
            bangsal_list = self.bangsal_repo.get_available_bangsal(min_beds)
            
            summaries = []
            for bangsal in bangsal_list:
                summaries.append(BangsalSummary(
                    id=bangsal.id,
                    nama_bangsal=bangsal.nama_bangsal,
                    kode_bangsal=bangsal.kode_bangsal,
                    kapasitas_total=bangsal.kapasitas_total,
                    tempat_tidur_tersedia=bangsal.tempat_tidur_tersedia,
                    tempat_tidur_terisi=bangsal.tempat_tidur_terisi,
                    occupancy_rate=bangsal.occupancy_rate,
                    jenis_bangsal=bangsal.jenis_bangsal,
                    is_active=bangsal.is_active,
                    is_emergency_ready=bangsal.is_emergency_ready
                ))
            
            return summaries
            
        except Exception as e:
            logger.error(f"Error getting available bangsal: {str(e)}")
            raise

    async def get_department_bangsal(self, departemen: str) -> List[BangsalSummary]:
        """Get all bangsal in a department"""
        try:
            bangsal_list = self.bangsal_repo.get_bangsal_by_department(departemen)
            
            summaries = []
            for bangsal in bangsal_list:
                summaries.append(BangsalSummary(
                    id=bangsal.id,
                    nama_bangsal=bangsal.nama_bangsal,
                    kode_bangsal=bangsal.kode_bangsal,
                    kapasitas_total=bangsal.kapasitas_total,
                    tempat_tidur_tersedia=bangsal.tempat_tidur_tersedia,
                    tempat_tidur_terisi=bangsal.tempat_tidur_terisi,
                    occupancy_rate=bangsal.occupancy_rate,
                    jenis_bangsal=bangsal.jenis_bangsal,
                    is_active=bangsal.is_active,
                    is_emergency_ready=bangsal.is_emergency_ready
                ))
            
            return summaries
            
        except Exception as e:
            logger.error(f"Error getting department bangsal: {str(e)}")
            raise

    # Statistics and Analytics
    async def get_occupancy_statistics(self) -> OccupancyStats:
        """Get overall occupancy statistics"""
        try:
            stats = self.bangsal_repo.get_occupancy_statistics()
            return OccupancyStats(**stats)
            
        except Exception as e:
            logger.error(f"Error getting occupancy statistics: {str(e)}")
            raise

    async def get_department_statistics(self) -> List[Dict[str, Any]]:
        """Get statistics by department"""
        try:
            return self.bangsal_repo.get_department_statistics()
            
        except Exception as e:
            logger.error(f"Error getting department statistics: {str(e)}")
            raise

    # Room Management
    async def get_bangsal_rooms(self, bangsal_id: int) -> List[KamarBangsalResponse]:
        """Get all rooms in a bangsal"""
        try:
            rooms = self.kamar_repo.get_kamar_by_bangsal(bangsal_id)
            
            responses = []
            for room in rooms:
                room_dict = room.__dict__.copy()
                room_dict['is_available'] = room.is_available
                room_dict['available_beds'] = room.available_beds
                responses.append(KamarBangsalResponse(**room_dict))
            
            return responses
            
        except Exception as e:
            logger.error(f"Error getting rooms for bangsal {bangsal_id}: {str(e)}")
            raise

    async def get_available_rooms(self, bangsal_id: int) -> List[KamarBangsalResponse]:
        """Get available rooms in a bangsal"""
        try:
            rooms = self.kamar_repo.get_available_kamar(bangsal_id)
            
            responses = []
            for room in rooms:
                room_dict = room.__dict__.copy()
                room_dict['is_available'] = room.is_available
                room_dict['available_beds'] = room.available_beds
                responses.append(KamarBangsalResponse(**room_dict))
            
            return responses
            
        except Exception as e:
            logger.error(f"Error getting available rooms for bangsal {bangsal_id}: {str(e)}")
            raise

    # Helper Methods
    async def _sync_room_capacities(self, bangsal_id: int):
        """Synchronize room capacities with bangsal total"""
        try:
            bangsal = self.bangsal_repo.get_bangsal_by_id(bangsal_id, include_rooms=True)
            if bangsal and bangsal.kamar_list:
                bangsal.update_capacity_from_rooms()
                self.db.commit()
                
        except Exception as e:
            logger.error(f"Error syncing room capacities for bangsal {bangsal_id}: {str(e)}")

    async def validate_bangsal_data(self, bangsal_data: BangsalCreate) -> List[str]:
        """Validate bangsal data and return list of errors"""
        errors = []
        
        # Check capacity logic
        if bangsal_data.kapasitas_total < 0:
            errors.append("Kapasitas total tidak boleh negatif")
        
        if bangsal_data.jumlah_kamar < 0:
            errors.append("Jumlah kamar tidak boleh negatif")
        
        # Check if kode already exists
        existing = self.bangsal_repo.get_bangsal_by_kode(bangsal_data.kode_bangsal)
        if existing:
            errors.append(f"Kode bangsal '{bangsal_data.kode_bangsal}' sudah ada")
        
        # Validate JSON facilities
        if bangsal_data.fasilitas:
            try:
                json.loads(bangsal_data.fasilitas)
            except json.JSONDecodeError:
                errors.append("Format fasilitas tidak valid (harus JSON)")
        
        return errors