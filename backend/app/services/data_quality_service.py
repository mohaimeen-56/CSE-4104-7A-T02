from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.sale import Sale
from app.schemas.analytics import DataQualityReport


class DataQualityService:
    """Detects missing/suspicious sale timestamps and reports overall timestamp coverage,
    per SalesIQ's requirement that the system surface real data-quality numbers rather than
    silently trusting every row."""

    @staticmethod
    def get_report(db: Session) -> DataQualityReport:
        total = db.query(func.count(Sale.id)).scalar() or 0
        estimated = db.query(func.count(Sale.id)).filter(Sale.is_estimated_time.is_(True)).scalar() or 0
        captured = total - estimated

        null_or_invalid = db.query(func.count(Sale.id)).filter(Sale.sale_datetime.is_(None)).scalar() or 0

        now = datetime.now(timezone.utc)
        future_dated = db.query(func.count(Sale.id)).filter(Sale.sale_datetime > now).scalar() or 0

        # Exact-timestamp duplicates: rows sharing the identical sale_datetime with >=1 other row.
        dup_rows = (
            db.query(Sale.sale_datetime, func.count(Sale.id).label("cnt"))
            .group_by(Sale.sale_datetime)
            .having(func.count(Sale.id) > 1)
            .all()
        )
        duplicate_count = sum(cnt - 1 for _, cnt in dup_rows)

        last_import = db.query(func.max(Sale.created_at)).scalar()

        coverage_pct = round((captured / total * 100), 1) if total > 0 else 100.0

        # Anomalies are computed lazily by the caller (ml.anomaly_detector) to avoid this
        # module depending on the full anomaly-detection pipeline for a simple count.
        anomaly_count = 0

        return DataQualityReport(
            total_records=total,
            captured_timestamps=captured,
            estimated_timestamps=estimated,
            timestamp_coverage_pct=coverage_pct,
            null_or_invalid_count=null_or_invalid,
            future_dated_count=future_dated,
            duplicate_exact_timestamp_count=duplicate_count,
            last_import_at=last_import.isoformat() if last_import else None,
            anomaly_count=anomaly_count,
        )
