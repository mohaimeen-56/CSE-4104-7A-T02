import csv
import io
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException, status
from app.models.sale import Sale
from app.models.product import Product
from app.models.region import Region
from app.schemas.sale import CsvUploadResponse, CsvRowError
from app.core.timeutil import build_sale_datetime

REQUIRED_COLUMNS = ["product_id", "region_id", "quantity", "unit_price", "sale_date"]
OPTIONAL_COLUMNS = ["sale_time"]  # e.g. "14:30" or "14:30:00" - omitted rows get a flagged estimated time


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

            # Validate product_id
            try:
                prod_id = int(row.get("product_id", ""))
                if prod_id not in existing_product_ids:
                    errors.append(CsvRowError(row=row_num, message=f"Product ID {prod_id} does not exist in database.", data=raw_row))
                    continue
            except (ValueError, TypeError):
                errors.append(CsvRowError(row=row_num, message=f"Invalid product_id '{row.get('product_id')}'. Must be an integer.", data=raw_row))
                continue

            # Validate region_id
            try:
                reg_id = int(row.get("region_id", ""))
                if reg_id not in existing_region_ids:
                    errors.append(CsvRowError(row=row_num, message=f"Region ID {reg_id} does not exist in database.", data=raw_row))
                    continue
            except (ValueError, TypeError):
                errors.append(CsvRowError(row=row_num, message=f"Invalid region_id '{row.get('region_id')}'. Must be an integer.", data=raw_row))
                continue

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

        return CsvUploadResponse(
            total_rows=total_rows,
            imported_rows=imported_rows,
            failed_rows=len(errors),
            errors=errors[:50]  # Cap error list to prevent huge payloads
        )
