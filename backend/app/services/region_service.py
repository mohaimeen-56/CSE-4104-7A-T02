from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.region import Region
from app.models.sale import Sale
from app.schemas.region import RegionCreate, RegionUpdate


class RegionService:
    @staticmethod
    def get_all(db: Session) -> List[Region]:
        return db.query(Region).order_by(Region.name.asc()).all()

    @staticmethod
    def get_by_id(db: Session, region_id: int) -> Optional[Region]:
        return db.query(Region).filter(Region.id == region_id).first()

    @staticmethod
    def create(db: Session, region_in: RegionCreate) -> Region:
        region = Region(
            name=region_in.name.strip(),
            country=region_in.country.strip() if region_in.country else "Bangladesh",
        )
        db.add(region)
        db.commit()
        db.refresh(region)
        return region

    @staticmethod
    def update(db: Session, region_id: int, region_in: RegionUpdate) -> Region:
        region = RegionService.get_by_id(db, region_id)
        if not region:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Region not found")

        if region_in.name is not None:
            region.name = region_in.name.strip()
        if region_in.country is not None:
            region.country = region_in.country.strip()

        db.add(region)
        db.commit()
        db.refresh(region)
        return region

    @staticmethod
    def delete(db: Session, region_id: int) -> bool:
        region = RegionService.get_by_id(db, region_id)
        if not region:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Region not found")

        sales_count = db.query(Sale).filter(Sale.region_id == region_id).count()
        if sales_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete region '{region.name}' because it has {sales_count} associated sales records."
            )

        db.delete(region)
        db.commit()
        return True
