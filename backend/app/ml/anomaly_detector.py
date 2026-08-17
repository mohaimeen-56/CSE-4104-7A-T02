from typing import List, Dict, Any, Optional
from datetime import date, datetime, timedelta
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.sale import Sale
from app.models.product import Product
from app.models.region import Region
from app.schemas.ai import AnomalyItem


class AnomalyDetector:
    @staticmethod
    def detect_anomalies(
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        z_threshold: float = 1.8
    ) -> List[AnomalyItem]:
        anomalies: List[AnomalyItem] = []

        # 1. Daily Sales Spikes & Drops by Region
        sales_by_date_region = (
            db.query(
                Sale.sale_date,
                Region.name.label("region_name"),
                func.sum(Sale.total_price).label("daily_rev"),
                func.sum(Sale.quantity).label("daily_units"),
            )
            .join(Region, Sale.region_id == Region.id)
            .group_by(Sale.sale_date, Region.name)
            .order_by(Sale.sale_date.asc())
            .all()
        )

        # Group data per region
        region_history: Dict[str, List[Dict[str, Any]]] = {}
        for row in sales_by_date_region:
            reg = row[1]
            if reg not in region_history:
                region_history[reg] = []
            region_history[reg].append({
                "date": row[0],
                "revenue": float(row[2]),
                "units": int(row[3])
            })

        # Calculate z-scores and detect rolling drops / spikes
        for reg_name, points in region_history.items():
            if len(points) < 3:
                continue

            revs = np.array([p["revenue"] for p in points])
            mean_rev = float(np.mean(revs))
            std_rev = float(np.std(revs)) if np.std(revs) > 0 else (mean_rev * 0.1)

            for p in points:
                # filter by date if provided
                if start_date and p["date"] < start_date:
                    continue
                if end_date and p["date"] > end_date:
                    continue

                diff = p["revenue"] - mean_rev
                z_score = diff / std_rev if std_rev > 0 else 0.0

                if z_score > z_threshold:
                    dev_pct = round(((p["revenue"] - mean_rev) / mean_rev) * 100, 1) if mean_rev > 0 else 100.0
                    anomalies.append(
                        AnomalyItem(
                            id=f"spike-{reg_name}-{p['date']}",
                            date=p["date"].strftime("%Y-%m-%d"),
                            title=f"Sales Spike Detected — {reg_name}",
                            description=f"Revenue spiked to ৳{p['revenue']:,.2f} ({dev_pct}% above baseline average of ৳{mean_rev:,.2f}).",
                            metric="Revenue Spike",
                            actual_value=p["revenue"],
                            expected_value=round(mean_rev, 2),
                            deviation_pct=dev_pct,
                            severity="medium" if z_score < 2.5 else "high",
                            type="spike",
                        )
                    )
                elif z_score < -z_threshold:
                    dev_pct = round(((p["revenue"] - mean_rev) / mean_rev) * 100, 1) if mean_rev > 0 else -100.0
                    anomalies.append(
                        AnomalyItem(
                            id=f"drop-{reg_name}-{p['date']}",
                            date=p["date"].strftime("%Y-%m-%d"),
                            title=f"Revenue Drop Alert — {reg_name}",
                            description=f"Sales dropped significantly on {p['date'].strftime('%b %d, %Y')} compared to baseline. Recommend reviewing regional stock and promotions.",
                            metric="Revenue Drop",
                            actual_value=p["revenue"],
                            expected_value=round(mean_rev, 2),
                            deviation_pct=dev_pct,
                            severity="high",
                            type="drop",
                        )
                    )

        # 2. Product-specific anomalies (e.g. abrupt decline or low sales volume)
        products = db.query(Product).all()
        for prod in products:
            if prod.stock < 20:
                anomalies.append(
                    AnomalyItem(
                        id=f"stock-{prod.id}",
                        date=datetime.now().strftime("%Y-%m-%d"),
                        title=f"Low Stock Alert — {prod.name} ({prod.category or 'General'})",
                        description=f"Stock is down to {prod.stock} units, below the 20-unit reorder threshold across regional warehouses.",
                        metric="Inventory Level",
                        actual_value=float(prod.stock),
                        expected_value=20.0,
                        deviation_pct=round(((prod.stock - 20) / 20) * 100, 1),
                        severity="high" if prod.stock <= 5 else "medium",
                        type="stock",
                    )
                )

        return anomalies
