from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.region import RegionCreate, RegionUpdate, RegionResponse
from app.schemas.common import APIResponse
from app.services.region_service import RegionService
from app.core.deps import require_manager_or_admin, require_admin
from app.models.user import User

router = APIRouter(prefix="/regions", tags=["Regions"])


@router.get("", response_model=APIResponse[List[RegionResponse]])
def get_regions(db: Session = Depends(get_db)):
    regions = RegionService.get_all(db)
    return APIResponse(
        success=True,
        message="Regions retrieved successfully",
        data=[RegionResponse.model_validate(r) for r in regions]
    )


@router.get("/{region_id}", response_model=APIResponse[RegionResponse])
def get_region_by_id(region_id: int, db: Session = Depends(get_db)):
    region = RegionService.get_by_id(db, region_id)
    if not region:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Region not found")
    return APIResponse(
        success=True,
        message="Region found",
        data=RegionResponse.model_validate(region)
    )


@router.post("", response_model=APIResponse[RegionResponse], status_code=status.HTTP_201_CREATED)
def create_region(
    region_in: RegionCreate,
    current_user: User = Depends(require_manager_or_admin),
    db: Session = Depends(get_db)
):
    region = RegionService.create(db, region_in)
    return APIResponse(
        success=True,
        message="Region created successfully",
        data=RegionResponse.model_validate(region)
    )


@router.put("/{region_id}", response_model=APIResponse[RegionResponse])
def update_region(
    region_id: int,
    region_in: RegionUpdate,
    current_user: User = Depends(require_manager_or_admin),
    db: Session = Depends(get_db)
):
    region = RegionService.update(db, region_id, region_in)
    return APIResponse(
        success=True,
        message="Region updated successfully",
        data=RegionResponse.model_validate(region)
    )


@router.delete("/{region_id}", response_model=APIResponse[dict])
def delete_region(
    region_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    RegionService.delete(db, region_id)
    return APIResponse(
        success=True,
        message="Region deleted successfully",
        data={"region_id": region_id}
    )
