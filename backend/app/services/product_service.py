from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.product import Product
from app.models.sale import Sale
from app.schemas.product import ProductCreate, ProductUpdate


class ProductService:
    @staticmethod
    def get_all(db: Session) -> List[Product]:
        return db.query(Product).order_by(Product.name.asc()).all()

    @staticmethod
    def get_by_id(db: Session, product_id: int) -> Optional[Product]:
        return db.query(Product).filter(Product.id == product_id).first()

    @staticmethod
    def create(db: Session, product_in: ProductCreate) -> Product:
        product = Product(
            name=product_in.name.strip(),
            category=product_in.category.strip() if product_in.category else None,
            subcategory=product_in.subcategory.strip() if product_in.subcategory else None,
            brand=product_in.brand.strip() if product_in.brand else None,
            sku=product_in.sku.strip() if product_in.sku else None,
            description=product_in.description.strip() if product_in.description else None,
            price=product_in.price,
            cost=product_in.cost,
            stock=product_in.stock,
            production_level=product_in.production_level,
            is_active=product_in.is_active,
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def update(db: Session, product_id: int, product_in: ProductUpdate) -> Product:
        product = ProductService.get_by_id(db, product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        if product_in.name is not None:
            product.name = product_in.name.strip()
        if product_in.category is not None:
            product.category = product_in.category.strip()
        if product_in.subcategory is not None:
            product.subcategory = product_in.subcategory.strip()
        if product_in.brand is not None:
            product.brand = product_in.brand.strip()
        if product_in.sku is not None:
            product.sku = product_in.sku.strip()
        if product_in.description is not None:
            product.description = product_in.description.strip()
        if product_in.price is not None:
            product.price = product_in.price
        if product_in.cost is not None:
            product.cost = product_in.cost
        if product_in.stock is not None:
            product.stock = product_in.stock
        if product_in.production_level is not None:
            product.production_level = product_in.production_level
        if product_in.is_active is not None:
            product.is_active = product_in.is_active

        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def delete(db: Session, product_id: int) -> bool:
        product = ProductService.get_by_id(db, product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        # Check for sales foreign key constraint
        sales_count = db.query(Sale).filter(Sale.product_id == product_id).count()
        if sales_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete product '{product.name}' because it has {sales_count} associated sales records."
            )

        db.delete(product)
        db.commit()
        return True
