from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.schemas.common import APIResponse
from app.services.product_service import ProductService
from app.core.deps import get_current_user, require_manager_or_admin, require_admin
from app.models.user import User

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=APIResponse[List[ProductResponse]])
def get_products(db: Session = Depends(get_db)):
    products = ProductService.get_all(db)
    return APIResponse(
        success=True,
        message="Products retrieved successfully",
        data=[ProductResponse.model_validate(p) for p in products]
    )


@router.get("/{product_id}", response_model=APIResponse[ProductResponse])
def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
    product = ProductService.get_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return APIResponse(
        success=True,
        message="Product found",
        data=ProductResponse.model_validate(product)
    )


@router.post("", response_model=APIResponse[ProductResponse], status_code=status.HTTP_201_CREATED)
def create_product(
    product_in: ProductCreate,
    current_user: User = Depends(require_manager_or_admin),
    db: Session = Depends(get_db)
):
    product = ProductService.create(db, product_in)
    return APIResponse(
        success=True,
        message="Product created successfully",
        data=ProductResponse.model_validate(product)
    )


@router.put("/{product_id}", response_model=APIResponse[ProductResponse])
def update_product(
    product_id: int,
    product_in: ProductUpdate,
    current_user: User = Depends(require_manager_or_admin),
    db: Session = Depends(get_db)
):
    product = ProductService.update(db, product_id, product_in)
    return APIResponse(
        success=True,
        message="Product updated successfully",
        data=ProductResponse.model_validate(product)
    )


@router.delete("/{product_id}", response_model=APIResponse[dict])
def delete_product(
    product_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    ProductService.delete(db, product_id)
    return APIResponse(
        success=True,
        message="Product deleted successfully",
        data={"product_id": product_id}
    )
