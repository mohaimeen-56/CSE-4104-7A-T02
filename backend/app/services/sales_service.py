from typing import Optional, List, Tuple
from datetime import date
from decimal import Decimal
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_, desc, asc
from fastapi import HTTPException, status
from app.models.sale import Sale
from app.models.product import Product
from app.models.region import Region
from app.models.user import User
from app.schemas.sale import SaleCreate, SaleUpdate
from app.core.timeutil import build_sale_datetime


class SalesService:
    @staticmethod
    def get_by_id(db: Session, sale_id: int) -> Optional[Sale]:
        return (
            db.query(Sale)
            .options(
                joinedload(Sale.product),
                joinedload(Sale.region),
                joinedload(Sale.user),
            )
            .filter(Sale.id == sale_id)
            .first()
        )

    @staticmethod
    def list_sales(
        db: Session,
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None,
        region_id: Optional[int] = None,
        product_id: Optional[int] = None,
        category: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        sort_by: str = "sale_date",
        sort_order: str = "desc",
    ) -> Tuple[List[Sale], int]:
        query = (
            db.query(Sale)
            .join(Product, Sale.product_id == Product.id)
            .join(Region, Sale.region_id == Region.id)
            .outerjoin(User, Sale.user_id == User.id)
            .options(
                joinedload(Sale.product),
                joinedload(Sale.region),
                joinedload(Sale.user),
            )
        )

        # Filters
        if region_id:
            query = query.filter(Sale.region_id == region_id)
        if product_id:
            query = query.filter(Sale.product_id == product_id)
        if category:
            query = query.filter(Product.category.ilike(f"%{category}%"))
        if start_date:
            query = query.filter(Sale.sale_date >= start_date)
        if end_date:
            query = query.filter(Sale.sale_date <= end_date)

        # Free-text Search across product name, region name, category, or date
        if search and search.strip():
            term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Product.name.ilike(term),
                    Product.category.ilike(term),
                    Region.name.ilike(term),
                    User.name.ilike(term),
                )
            )

        total = query.count()

        # Sorting
        sort_column = getattr(Sale, sort_by, Sale.sale_date)
        if sort_order.lower() == "asc":
            query = query.order_by(asc(sort_column), asc(Sale.id))
        else:
            query = query.order_by(desc(sort_column), desc(Sale.id))

        # Pagination
        offset = (page - 1) * page_size
        sales = query.offset(offset).limit(page_size).all()

        return sales, total

    @staticmethod
    def create(db: Session, sale_in: SaleCreate, user_id: Optional[int] = None) -> Sale:
        product = db.query(Product).filter(Product.id == sale_in.product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product with ID {sale_in.product_id} does not exist"
            )

        region = db.query(Region).filter(Region.id == sale_in.region_id).first()
        if not region:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Region with ID {sale_in.region_id} does not exist"
            )

        total_price = Decimal(sale_in.quantity) * Decimal(sale_in.unit_price)
        sale_datetime, is_estimated = build_sale_datetime(sale_in.sale_date, sale_in.sale_time)

        sale = Sale(
            user_id=user_id,
            product_id=sale_in.product_id,
            region_id=sale_in.region_id,
            quantity=sale_in.quantity,
            unit_price=sale_in.unit_price,
            total_price=total_price,
            sale_date=sale_in.sale_date,
            sale_datetime=sale_datetime,
            is_estimated_time=is_estimated,
        )
        db.add(sale)
        db.commit()
        db.refresh(sale)
        return SalesService.get_by_id(db, sale.id)

    @staticmethod
    def update(db: Session, sale_id: int, sale_in: SaleUpdate) -> Sale:
        sale = db.query(Sale).filter(Sale.id == sale_id).first()
        if not sale:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale record not found")

        if sale_in.product_id is not None:
            prod = db.query(Product).filter(Product.id == sale_in.product_id).first()
            if not prod:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid product ID")
            sale.product_id = sale_in.product_id

        if sale_in.region_id is not None:
            reg = db.query(Region).filter(Region.id == sale_in.region_id).first()
            if not reg:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid region ID")
            sale.region_id = sale_in.region_id

        if sale_in.quantity is not None:
            sale.quantity = sale_in.quantity
        if sale_in.unit_price is not None:
            sale.unit_price = sale_in.unit_price
        if sale_in.sale_date is not None or sale_in.sale_time is not None:
            new_date = sale_in.sale_date if sale_in.sale_date is not None else sale.sale_date
            sale.sale_date = new_date
            sale.sale_datetime, sale.is_estimated_time = build_sale_datetime(new_date, sale_in.sale_time)

        # Recalculate total_price reliably on the server
        sale.total_price = Decimal(sale.quantity) * Decimal(sale.unit_price)

        db.add(sale)
        db.commit()
        db.refresh(sale)
        return SalesService.get_by_id(db, sale.id)

    @staticmethod
    def delete(db: Session, sale_id: int) -> bool:
        sale = db.query(Sale).filter(Sale.id == sale_id).first()
        if not sale:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale record not found")
        db.delete(sale)
        db.commit()
        return True
