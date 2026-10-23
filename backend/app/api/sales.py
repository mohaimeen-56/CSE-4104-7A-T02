import math
from typing import Optional, List
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db
from app.schemas.sale import SaleCreate, SaleUpdate, SaleResponse, CsvUploadResponse
from app.schemas.common import APIResponse, PaginatedResponse, PaginationMeta
from app.services.sales_service import SalesService
from app.services.csv_service import CsvService
from app.core.deps import get_current_user, require_manager_or_admin, require_admin
from app.models.user import User
from app.models.sale import Sale
from app.models.product import Product
from app.models.notification import Notification
from app.models.ai_log import AILog

router = APIRouter(prefix="/sales", tags=["Sales"])


@router.get("", response_model=PaginatedResponse[SaleResponse])
def list_sales(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search across products, categories, regions"),
    region_id: Optional[int] = Query(None, description="Filter by region ID"),
    product_id: Optional[int] = Query(None, description="Filter by product ID"),
    category: Optional[str] = Query(None, description="Filter by category name"),
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    sort_by: str = Query("sale_date", description="Field to sort by"),
    sort_order: str = Query("desc", description="Sort order: 'asc' or 'desc'"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sales, total = SalesService.list_sales(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        region_id=region_id,
        product_id=product_id,
        category=category,
        start_date=start_date,
        end_date=end_date,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    total_pages = math.ceil(total / page_size) if total > 0 else 1

    return PaginatedResponse(
        success=True,
        message="Sales records retrieved",
        data=[SaleResponse.model_validate(s) for s in sales],
        pagination=PaginationMeta(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
        )
    )


@router.get("/{sale_id}", response_model=APIResponse[SaleResponse])
def get_sale(sale_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sale = SalesService.get_by_id(db, sale_id)
    if not sale:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale record not found")
    return APIResponse(
        success=True,
        message="Sale record found",
        data=SaleResponse.model_validate(sale)
    )


@router.post("", response_model=APIResponse[SaleResponse], status_code=status.HTTP_201_CREATED)
def create_sale(
    sale_in: SaleCreate,
    current_user: User = Depends(require_manager_or_admin),
    db: Session = Depends(get_db)
):
    sale = SalesService.create(db, sale_in, user_id=current_user.id)
    return APIResponse(
        success=True,
        message="Sale record created successfully",
        data=SaleResponse.model_validate(sale)
    )


@router.put("/{sale_id}", response_model=APIResponse[SaleResponse])
def update_sale(
    sale_id: int,
    sale_in: SaleUpdate,
    current_user: User = Depends(require_manager_or_admin),
    db: Session = Depends(get_db)
):
    sale = SalesService.update(db, sale_id, sale_in)
    return APIResponse(
        success=True,
        message="Sale record updated successfully",
        data=SaleResponse.model_validate(sale)
    )


class BulkDeleteRequest(BaseModel):
    ids: List[int]


@router.delete("/all", response_model=APIResponse[dict])
@router.post("/delete-all", response_model=APIResponse[dict])
def delete_all_sales(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Permanently delete ALL sales records and products. Admin only."""
    deleted_sales = db.query(Sale).delete(synchronize_session=False)
    deleted_products = db.query(Product).delete(synchronize_session=False)
    deleted_notifs = db.query(Notification).delete(synchronize_session=False)
    deleted_ai_logs = db.query(AILog).delete(synchronize_session=False)

    try:
        db.execute(text("ALTER SEQUENCE sales_id_seq RESTART WITH 1"))
        db.execute(text("ALTER SEQUENCE products_id_seq RESTART WITH 1"))
        db.execute(text("ALTER SEQUENCE notifications_id_seq RESTART WITH 1"))
        db.execute(text("ALTER SEQUENCE ai_logs_id_seq RESTART WITH 1"))
    except Exception:
        pass

    db.commit()
    return APIResponse(
        success=True,
        message=f"All {deleted_sales} sales and {deleted_products} products have been permanently deleted.",
        data={
            "deleted_count": deleted_sales,
            "deleted_sales": deleted_sales,
            "deleted_products": deleted_products,
            "deleted_notifications": deleted_notifs,
            "deleted_ai_logs": deleted_ai_logs,
        },
    )


@router.delete("/bulk", response_model=APIResponse[dict])
@router.post("/bulk-delete", response_model=APIResponse[dict])
def delete_selected_sales(
    payload: BulkDeleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Permanently delete a specific set of sales records by ID. Admin only."""
    if not payload.ids:
        raise HTTPException(status_code=400, detail="No IDs provided.")
    deleted_count = (
        db.query(Sale)
        .filter(Sale.id.in_(payload.ids))
        .delete(synchronize_session=False)
    )
    db.commit()
    return APIResponse(
        success=True,
        message=f"{deleted_count} sale(s) permanently deleted.",
        data={"deleted_count": deleted_count, "requested_ids": payload.ids},
    )


@router.delete("/{sale_id}", response_model=APIResponse[dict])
def delete_sale(
    sale_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    SalesService.delete(db, sale_id)
    return APIResponse(
        success=True,
        message="Sale record deleted successfully",
        data={"sale_id": sale_id}
    )


@router.post("/upload-csv", response_model=APIResponse[CsvUploadResponse])
async def upload_sales_csv(
    file: UploadFile = File(...),
    current_user: User = Depends(require_manager_or_admin),
    db: Session = Depends(get_db)
):
    result = await CsvService.import_sales_csv(file, db, user_id=current_user.id)
    return APIResponse(
        success=True,
        message=f"CSV processing complete: {result.imported_rows} rows imported, {result.failed_rows} rows failed.",
        data=result
    )
