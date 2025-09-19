# backend/api/v1/bangsal_router.py
"""
Bangsal API Router
RESTful endpoints for bangsal (hospital ward) management
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ...database.session import get_db
from ...services.bangsal_service import BangsalService
from ...schemas.bangsal import (
    BangsalCreate, BangsalUpdate, BangsalResponse, BangsalList, BangsalSummary,
    KamarBangsalCreate, KamarBangsalUpdate, KamarBangsalResponse,
    CapacityUpdate, OccupancyStats, BangsalFilter
)
from ...core.auth import get_current_user, require_role
from ...models.user import User

router = APIRouter(prefix="/bangsal", tags=["Bangsal Management"])

def get_bangsal_service(db: Session = Depends(get_db)) -> BangsalService:
    """Dependency to get bangsal service"""
    return BangsalService(db)

# Core CRUD Endpoints
@router.post("/", response_model=BangsalResponse, status_code=status.HTTP_201_CREATED)
async def create_bangsal(
    bangsal_data: BangsalCreate,
    current_user: User = Depends(require_role(["admin", "doctor"])),
    service: BangsalService = Depends(get_bangsal_service)
):
    """
    Create new bangsal
    
    Requires: Admin or Doctor role
    """
    try:
        return await service.create_bangsal(bangsal_data, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create bangsal")

@router.get("/", response_model=BangsalList)
async def get_bangsal_list(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    include_inactive: bool = Query(False, description="Include inactive bangsal"),
    search: Optional[str] = Query(None, description="Search term"),
    jenis_bangsal: Optional[str] = Query(None, description="Filter by jenis bangsal"),
    departemen: Optional[str] = Query(None, description="Filter by departemen"),
    is_emergency_ready: Optional[bool] = Query(None, description="Filter by emergency ready status"),
    min_available_beds: Optional[int] = Query(None, ge=0, description="Minimum available beds"),
    current_user: User = Depends(get_current_user),
    service: BangsalService = Depends(get_bangsal_service)
):
    """
    Get paginated list of bangsal with optional filters and search
    
    Requires: Any authenticated user
    """
    try:
        filters = None
        if any([jenis_bangsal, departemen, is_emergency_ready is not None, min_available_beds is not None]):
            filters = BangsalFilter(
                jenis_bangsal=jenis_bangsal,
                departemen=departemen,
                is_emergency_ready=is_emergency_ready,
                min_available_beds=min_available_beds
            )
        
        return await service.get_bangsal_list(
            page=page,
            per_page=per_page,
            include_inactive=include_inactive,
            search=search,
            filters=filters
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get bangsal list")

@router.get("/{bangsal_id}", response_model=BangsalResponse)
async def get_bangsal(
    bangsal_id: int,
    include_rooms: bool = Query(False, description="Include room details"),
    current_user: User = Depends(get_current_user),
    service: BangsalService = Depends(get_bangsal_service)
):
    """
    Get bangsal by ID
    
    Requires: Any authenticated user
    """
    bangsal = await service.get_bangsal(bangsal_id, include_rooms)
    if not bangsal:
        raise HTTPException(status_code=404, detail="Bangsal not found")
    return bangsal

@router.get("/kode/{kode_bangsal}", response_model=BangsalResponse)
async def get_bangsal_by_kode(
    kode_bangsal: str,
    current_user: User = Depends(get_current_user),
    service: BangsalService = Depends(get_bangsal_service)
):
    """
    Get bangsal by unique code
    
    Requires: Any authenticated user
    """
    bangsal = await service.get_bangsal_by_kode(kode_bangsal)
    if not bangsal:
        raise HTTPException(status_code=404, detail="Bangsal not found")
    return bangsal

@router.put("/{bangsal_id}", response_model=BangsalResponse)
async def update_bangsal(
    bangsal_id: int,
    bangsal_data: BangsalUpdate,
    current_user: User = Depends(require_role(["admin", "doctor", "nurse"])),
    service: BangsalService = Depends(get_bangsal_service)
):
    """
    Update bangsal information
    
    Requires: Admin, Doctor, or Nurse role
    """
    try:
        bangsal = await service.update_bangsal(bangsal_id, bangsal_data, current_user.id)
        if not bangsal:
            raise HTTPException(status_code=404, detail="Bangsal not found")
        return bangsal
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to update bangsal")

@router.delete("/{bangsal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bangsal(
    bangsal_id: int,
    hard_delete: bool = Query(False, description="Permanently delete (hard delete)"),
    current_user: User = Depends(require_role(["admin"])),
    service: BangsalService = Depends(get_bangsal_service)
):
    """
    Delete bangsal (soft delete by default)
    
    Requires: Admin role
    """
    success = await service.delete_bangsal(bangsal_id, hard_delete)
    if not success:
        raise HTTPException(status_code=404, detail="Bangsal not found")

# Capacity Management Endpoints
@router.put("/{bangsal_id}/capacity", response_model=BangsalResponse)
async def update_bed_capacity(
    bangsal_id: int,
    capacity_data: CapacityUpdate,
    current_user: User = Depends(require_role(["admin", "doctor", "nurse"])),
    service: BangsalService = Depends(get_bangsal_service)
):
    """
    Update bed capacity/occupancy for bangsal
    
    Requires: Admin, Doctor, or Nurse role
    """
    try:
        bangsal = await service.update_bed_capacity(bangsal_id, capacity_data)
        if not bangsal:
            raise HTTPException(status_code=404, detail="Bangsal not found")
        return bangsal
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to update capacity")

@router.post("/bulk-capacity", response_model=List[BangsalResponse])
async def bulk_update_capacity(
    capacity_updates: List[Dict[str, Any]],
    current_user: User = Depends(require_role(["admin", "doctor", "nurse"])),
    service: BangsalService = Depends(get_bangsal_service)
):
    """
    Bulk update bed capacity for multiple bangsal
    
    Expected format:
    [
        {"bangsal_id": 1, "tempat_tidur_terisi": 10},
        {"bangsal_id": 2, "tempat_tidur_terisi": 15}
    ]
    
    Requires: Admin, Doctor, or Nurse role
    """
    try:
        return await service.bulk_update_capacity(capacity_updates)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to bulk update capacity")

# Specialized Query Endpoints
@router.get("/emergency/ready", response_model=List[BangsalSummary])
async def get_emergency_ready_bangsal(
    current_user: User = Depends(get_current_user),
    service: BangsalService = Depends(get_bangsal_service)
):
    """
    Get bangsal ready for emergency admissions
    
    Requires: Any authenticated user
    """
    return await service.get_emergency_ready_bangsal()

@router.get("/available/beds", response_model=List[BangsalSummary])
async def get_available_bangsal(
    min_beds: int = Query(1, ge=1, description="Minimum required beds"),
    current_user: User = Depends(get_current_user),
    service: BangsalService = Depends(get_bangsal_service)
):
    """
    Get bangsal with available beds
    
    Requires: Any authenticated user
    """
    return await service.get_available_bangsal(min_beds)

@router.get("/department/{departemen}", response_model=List[BangsalSummary])
async def get_department_bangsal(
    departemen: str,
    current_user: User = Depends(get_current_user),
    service: BangsalService = Depends(get_bangsal_service)
):
    """
    Get all bangsal in a specific department
    
    Requires: Any authenticated user
    """
    return await service.get_department_bangsal(departemen)

# Statistics and Analytics Endpoints
@router.get("/statistics/occupancy", response_model=OccupancyStats)
async def get_occupancy_statistics(
    current_user: User = Depends(get_current_user),
    service: BangsalService = Depends(get_bangsal_service)
):
    """
    Get overall occupancy statistics
    
    Requires: Any authenticated user
    """
    return await service.get_occupancy_statistics()

@router.get("/statistics/department", response_model=List[Dict[str, Any]])
async def get_department_statistics(
    current_user: User = Depends(get_current_user),
    service: BangsalService = Depends(get_bangsal_service)
):
    """
    Get statistics by department
    
    Requires: Any authenticated user
    """
    return await service.get_department_statistics()

# Room Management Endpoints
@router.get("/{bangsal_id}/rooms", response_model=List[KamarBangsalResponse])
async def get_bangsal_rooms(
    bangsal_id: int,
    available_only: bool = Query(False, description="Only return available rooms"),
    current_user: User = Depends(get_current_user),
    service: BangsalService = Depends(get_bangsal_service)
):
    """
    Get all rooms in a bangsal
    
    Requires: Any authenticated user
    """
    if available_only:
        return await service.get_available_rooms(bangsal_id)
    else:
        return await service.get_bangsal_rooms(bangsal_id)

@router.post("/{bangsal_id}/rooms", response_model=KamarBangsalResponse, status_code=status.HTTP_201_CREATED)
async def create_room(
    bangsal_id: int,
    room_data: KamarBangsalCreate,
    current_user: User = Depends(require_role(["admin", "doctor"])),
    service: BangsalService = Depends(get_bangsal_service)
):
    """
    Create new room in bangsal
    
    Requires: Admin or Doctor role
    """
    try:
        # Ensure room is assigned to correct bangsal
        room_data.bangsal_id = bangsal_id
        room = service.kamar_repo.create_kamar(room_data)
        
        # Convert to response format
        room_dict = room.__dict__.copy()
        room_dict['is_available'] = room.is_available
        room_dict['available_beds'] = room.available_beds
        
        return KamarBangsalResponse(**room_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create room")

# Utility Endpoints
@router.get("/types/jenis", response_model=List[str])
async def get_bangsal_types(
    current_user: User = Depends(get_current_user)
):
    """
    Get list of available bangsal types
    
    Requires: Any authenticated user
    """
    return ["VIP", "Kelas I", "Kelas II", "Kelas III", "ICU", "NICU", "PICU", "HCU", "Isolasi"]

@router.get("/types/departments", response_model=List[str])
async def get_departments(
    current_user: User = Depends(get_current_user),
    service: BangsalService = Depends(get_bangsal_service)
):
    """
    Get list of departments that have bangsal
    
    Requires: Any authenticated user
    """
    try:
        # Get unique departments from existing bangsal
        bangsal_list = service.bangsal_repo.get_all_bangsal(skip=0, limit=1000)
        departments = list(set([b.departemen for b in bangsal_list if b.departemen]))
        return sorted(departments)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get departments")

@router.post("/{bangsal_id}/validate", response_model=Dict[str, Any])
async def validate_bangsal(
    bangsal_id: int,
    current_user: User = Depends(require_role(["admin", "doctor"])),
    service: BangsalService = Depends(get_bangsal_service)
):
    """
    Validate bangsal data and capacity consistency
    
    Requires: Admin or Doctor role
    """
    try:
        bangsal = await service.get_bangsal(bangsal_id)
        if not bangsal:
            raise HTTPException(status_code=404, detail="Bangsal not found")
        
        # Check capacity consistency
        rooms = await service.get_bangsal_rooms(bangsal_id)
        total_room_capacity = sum(room.kapasitas_kamar for room in rooms)
        total_room_occupied = sum(room.tempat_tidur_terisi for room in rooms)
        
        validation_result = {
            "bangsal_id": bangsal_id,
            "bangsal_capacity": bangsal.kapasitas_total,
            "room_total_capacity": total_room_capacity,
            "bangsal_occupied": bangsal.tempat_tidur_terisi,
            "room_total_occupied": total_room_occupied,
            "capacity_consistent": bangsal.kapasitas_total == total_room_capacity,
            "occupancy_consistent": bangsal.tempat_tidur_terisi == total_room_occupied,
            "issues": []
        }
        
        if not validation_result["capacity_consistent"]:
            validation_result["issues"].append("Total kapasitas bangsal tidak sesuai dengan total kapasitas kamar")
        
        if not validation_result["occupancy_consistent"]:
            validation_result["issues"].append("Total okupansi bangsal tidak sesuai dengan total okupansi kamar")
        
        validation_result["is_valid"] = len(validation_result["issues"]) == 0
        
        return validation_result
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to validate bangsal")