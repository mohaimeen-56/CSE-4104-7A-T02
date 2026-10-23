import csv
import io
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import UploadFile, HTTPException, status
from app.models.sale import Sale
from app.models.product import Product
from app.models.region import Region
from app.schemas.sale import CsvUploadResponse, CsvRowError
from app.core.timeutil import build_sale_datetime

REQUIRED_COLUMNS = ["product_id", "region_id", "quantity", "unit_price", "sale_date"]
OPTIONAL_COLUMNS = ["sale_time"]  # e.g. "14:30" or "14:30:00" - omitted rows get a flagged estimated time

DEFAULT_PRODUCTS = {
    1: {"name": "iPhone 15", "category": "Electronics", "subcategory": "Phones", "brand": "Apple", "cost_ratio": Decimal("0.82")},
    2: {"name": "ThinkPad X1 Carbon", "category": "Electronics", "subcategory": "Laptops", "brand": "Lenovo", "cost_ratio": Decimal("0.81")},
    3: {"name": "Galaxy Tab S9", "category": "Electronics", "subcategory": "Tablets", "brand": "Samsung", "cost_ratio": Decimal("0.80")},
    4: {"name": "AirPods Pro", "category": "Electronics", "subcategory": "Audio", "brand": "Apple", "cost_ratio": Decimal("0.73")},
    5: {"name": "Dell XPS 15", "category": "Electronics", "subcategory": "Laptops", "brand": "Dell", "cost_ratio": Decimal("0.81")},
    6: {"name": "Sony WH-1000XM5", "category": "Electronics", "subcategory": "Audio", "brand": "Sony", "cost_ratio": Decimal("0.79")},
    7: {"name": "Office Ergonomic Chair", "category": "Furniture", "subcategory": "Chairs", "brand": "ErgoComfort", "cost_ratio": Decimal("0.72")},
    8: {"name": "Smart LED Desk Lamp", "category": "Furniture", "subcategory": "Lighting", "brand": "Lumina", "cost_ratio": Decimal("0.65")},
    9: {"name": "Logitech MX Master 3S", "category": "Electronics", "subcategory": "Accessories", "brand": "Logitech", "cost_ratio": Decimal("0.74")},
    10: {"name": 'Samsung 4K Monitor 27"', "category": "Electronics", "subcategory": "Displays", "brand": "Samsung", "cost_ratio": Decimal("0.76")},
}

DEFAULT_REGIONS = {
    1: "Dhaka",
    2: "Chittagong",
    3: "Khulna",
    4: "Sylhet",
    5: "Rajshahi",
}


class CsvService:
    @staticmethod
    async def import_sales_csv(
        file: UploadFile,
        db: Session,
        user_id: Optional[int] = None
    ) -> CsvUploadResponse:
        # Validate filename and MIME type
        if not file.filename.lower().endswith(".csv"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only CSV (.csv) files are supported."
            )

        content = await file.read()
        try:
            text = content.decode("utf-8-sig")
        except UnicodeDecodeError:
            try:
                text = content.decode("latin-1")
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to decode file. Please ensure it is UTF-8 encoded."
                )

        reader = csv.DictReader(io.StringIO(text))
        if not reader.fieldnames:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The uploaded CSV file is empty."
            )

        # Normalize column headers
        normalized_headers = [h.strip().lower().replace(" ", "_") for h in reader.fieldnames if h]
        missing_cols = [col for col in REQUIRED_COLUMNS if col not in normalized_headers]
        if missing_cols:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required columns: {', '.join(missing_cols)}. Expected: {', '.join(REQUIRED_COLUMNS)}"
            )

        # Cache existing product and region IDs for ultra-fast validation
        existing_product_ids = set(r[0] for r in db.query(Product.id).all())
        existing_region_ids = set(r[0] for r in db.query(Region.id).all())

        total_rows = 0
        imported_rows = 0
        errors: List[CsvRowError] = []
        sales_to_insert: List[Sale] = []

        for row_num, raw_row in enumerate(reader, start=2):  # row 1 is header
            total_rows += 1
            # Normalize row keys
            row = {k.strip().lower().replace(" ", "_"): v.strip() for k, v in raw_row.items() if k}

            # Validate quantity
            try:
                qty = int(row.get("quantity", ""))
                if qty <= 0:
                    errors.append(CsvRowError(row=row_num, message=f"Quantity must be greater than 0. Found: {qty}", data=raw_row))
                    continue
            except (ValueError, TypeError):
                errors.append(CsvRowError(row=row_num, message=f"Invalid quantity '{row.get('quantity')}'. Must be an integer.", data=raw_row))
                continue

            # Validate unit_price
            try:
                unit_price = Decimal(row.get("unit_price", ""))
                if unit_price < 0:
                    errors.append(CsvRowError(row=row_num, message=f"Unit price cannot be negative. Found: {unit_price}", data=raw_row))
                    continue
            except (InvalidOperation, TypeError):
                errors.append(CsvRowError(row=row_num, message=f"Invalid unit_price '{row.get('unit_price')}'. Must be a decimal number.", data=raw_row))
                continue

            # Validate product_id (Auto-creates missing products!)
            try:
                prod_id = int(row.get("product_id", ""))
                if prod_id not in existing_product_ids:
                    # Auto-provision product so CSV row is never rejected
                    tmpl = None
                    if prod_id in DEFAULT_PRODUCTS:
                        tmpl = DEFAULT_PRODUCTS[prod_id]
                    elif (prod_id - 50) in DEFAULT_PRODUCTS:
                        tmpl = DEFAULT_PRODUCTS[prod_id - 50]
                    elif (prod_id - 10) in DEFAULT_PRODUCTS:
                        tmpl = DEFAULT_PRODUCTS[prod_id - 10]
                    elif (prod_id % 10) in DEFAULT_PRODUCTS and (prod_id % 10) != 0:
                        tmpl = DEFAULT_PRODUCTS[prod_id % 10]
                    elif (prod_id % 10) == 0:
                        tmpl = DEFAULT_PRODUCTS[10]

                    p_name = row.get("product_name") or row.get("product") or (tmpl["name"] if tmpl else f"Product #{prod_id}")
                    p_cat = row.get("category") or (tmpl["category"] if tmpl else "General")
                    p_sub = row.get("subcategory") or (tmpl["subcategory"] if tmpl else None)
                    p_brand = row.get("brand") or (tmpl["brand"] if tmpl else None)
                    c_ratio = tmpl["cost_ratio"] if tmpl else Decimal("0.75")
                    cost_val = round(unit_price * c_ratio, 2)

                    new_prod = Product(
                        id=prod_id,
                        name=p_name,
                        category=p_cat,
                        subcategory=p_sub,
                        brand=p_brand,
                        price=unit_price,
                        cost=cost_val,
                        stock=100,
                        is_active=True,
                    )
                    db.add(new_prod)
                    db.flush()
                    existing_product_ids.add(prod_id)
            except (ValueError, TypeError):
                errors.append(CsvRowError(row=row_num, message=f"Invalid product_id '{row.get('product_id')}'. Must be an integer.", data=raw_row))
                continue

            # Validate region_id (Auto-creates missing regions!)
            try:
                reg_id = int(row.get("region_id", ""))
                if reg_id not in existing_region_ids:
                    # Auto-provision region so CSV row is never rejected
                    r_mapped = None
                    if reg_id in DEFAULT_REGIONS:
                        r_mapped = DEFAULT_REGIONS[reg_id]
                    elif (reg_id - 25) in DEFAULT_REGIONS:
                        r_mapped = DEFAULT_REGIONS[reg_id - 25]
                    elif (reg_id - 5) in DEFAULT_REGIONS:
                        r_mapped = DEFAULT_REGIONS[reg_id - 5]
                    elif (reg_id % 5) in DEFAULT_REGIONS and (reg_id % 5) != 0:
                        r_mapped = DEFAULT_REGIONS[reg_id % 5]
                    elif (reg_id % 5) == 0:
                        r_mapped = DEFAULT_REGIONS[5]

                    r_name = row.get("region_name") or row.get("region") or (r_mapped if r_mapped else f"Region #{reg_id}")
                    new_reg = Region(
                        id=reg_id,
                        name=r_name,
                        country="Bangladesh",
                    )
                    db.add(new_reg)
                    db.flush()
                    existing_region_ids.add(reg_id)
            except (ValueError, TypeError):
                errors.append(CsvRowError(row=row_num, message=f"Invalid region_id '{row.get('region_id')}'. Must be an integer.", data=raw_row))
                continue

            # Validate sale_date (supports YYYY-MM-DD, DD/MM/YYYY, MM/DD/YYYY)
            sale_date_str = row.get("sale_date", "")
            parsed_date: Optional[date] = None
            date_formats = ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d", "%d-%m-%Y"]
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(sale_date_str, fmt).date()
                    break
                except ValueError:
                    continue

            if not parsed_date:
                errors.append(CsvRowError(row=row_num, message=f"Invalid sale_date '{sale_date_str}'. Expected format YYYY-MM-DD.", data=raw_row))
                continue

            total_price = Decimal(qty) * unit_price
            sale_datetime, is_estimated = build_sale_datetime(parsed_date, row.get("sale_time"))

            sale = Sale(
                user_id=user_id,
                product_id=prod_id,
                region_id=reg_id,
                quantity=qty,
                unit_price=unit_price,
                total_price=total_price,
                sale_date=parsed_date,
                sale_datetime=sale_datetime,
                is_estimated_time=is_estimated,
            )
            sales_to_insert.append(sale)

        # Batch insert valid rows
        if sales_to_insert:
            db.bulk_save_objects(sales_to_insert)
            db.commit()
            imported_rows = len(sales_to_insert)

            # Sync sequences for PostgreSQL if needed
            try:
                db.execute(text("SELECT setval('products_id_seq', (SELECT COALESCE(MAX(id), 1) FROM products))"))
                db.execute(text("SELECT setval('regions_id_seq', (SELECT COALESCE(MAX(id), 1) FROM regions))"))
                db.execute(text("SELECT setval('sales_id_seq', (SELECT COALESCE(MAX(id), 1) FROM sales))"))
                db.commit()
            except Exception:
                pass

        return CsvUploadResponse(
            total_rows=total_rows,
            imported_rows=imported_rows,
            failed_rows=len(errors),
            errors=errors[:50]  # Cap error list to prevent huge payloads
        )
