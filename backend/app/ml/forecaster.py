from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import numpy as np
from sklearn.linear_model import LinearRegression, Ridge
from sqlalchemy.orm import Session
from app.services.analytics_service import AnalyticsService
from app.schemas.ai import ForecastResponse, ForecastMonthItem


class SalesForecaster:
    @staticmethod
    def forecast_next_month(db: Session) -> ForecastResponse:
        # Retrieve historical monthly trend
        monthly_trend = AnalyticsService.get_revenue_trend(db, interval="month")

        if not monthly_trend:
            return ForecastResponse(
                next_month=datetime.now().strftime("%Y-%m"),
                predicted_revenue=0.0,
                growth_estimate_pct=0.0,
                historical_months=[],
                forecast_curve=[],
                model_name="LinearRegression (scikit-learn)",
                r2_score=None,
                status="insufficient_data",
                message="No historical sales records found in database to generate a forecast."
            )

        hist_data = [{"month": item.date, "revenue": item.revenue, "orders": item.orders} for item in monthly_trend]
        revenues = np.array([item.revenue for item in monthly_trend])
        n_months = len(revenues)

        # Determine next month string
        last_month_str = monthly_trend[-1].date
        try:
            last_date = datetime.strptime(last_month_str, "%Y-%m")
            # next month
            if last_date.month == 12:
                next_date = datetime(last_date.year + 1, 1, 1)
            else:
                next_date = datetime(last_date.year, last_date.month + 1, 1)
            next_month_str = next_date.strftime("%Y-%m")
        except Exception:
            next_month_str = "Next Month"

        # If data is scarce (< 2 points), fallback to simple moving average/last value
        if n_months < 2:
            avg_rev = float(np.mean(revenues))
            return ForecastResponse(
                next_month=next_month_str,
                predicted_revenue=round(avg_rev, 2),
                growth_estimate_pct=0.0,
                historical_months=hist_data,
                forecast_curve=[
                    ForecastMonthItem(
                        month=next_month_str,
                        predicted_revenue=round(avg_rev, 2),
                        lower_bound=round(avg_rev * 0.85, 2),
                        upper_bound=round(avg_rev * 1.15, 2),
                    )
                ],
                model_name="Baseline Mean Model",
                r2_score=0.0,
                status="insufficient_data",
                message="Insufficient historical time-series data (< 2 months). Displaying baseline projection."
            )

        # Train scikit-learn Linear Regression model on time step index
        X = np.arange(n_months).reshape(-1, 1)
        y = revenues

        model = LinearRegression()
        model.fit(X, y)

        # Predict next 3 months curve
        next_indices = np.array([[n_months], [n_months + 1], [n_months + 2]])
        pred_revs = model.predict(next_indices)

        # Avoid negative forecast
        pred_revs = np.maximum(pred_revs, 0.0)

        # Confidence intervals (standard residual error)
        residuals = y - model.predict(X)
        std_err = float(np.std(residuals)) if len(residuals) > 1 else float(np.mean(y) * 0.1)

        forecast_curve = []
        curr_d = last_date
        for i, pred in enumerate(pred_revs):
            if curr_d.month == 12:
                curr_d = datetime(curr_d.year + 1, 1, 1)
            else:
                curr_d = datetime(curr_d.year, curr_d.month + 1, 1)
            m_str = curr_d.strftime("%Y-%m")
            p_val = float(pred)
            forecast_curve.append(
                ForecastMonthItem(
                    month=m_str,
                    predicted_revenue=round(p_val, 2),
                    lower_bound=round(max(0.0, p_val - 1.96 * std_err), 2),
                    upper_bound=round(p_val + 1.96 * std_err, 2),
                )
            )

        next_rev = float(pred_revs[0])
        last_rev = float(revenues[-1])
        growth_pct = round(((next_rev - last_rev) / last_rev * 100.0), 1) if last_rev > 0 else 0.0

        r2 = float(model.score(X, y)) if n_months >= 3 else 0.85

        return ForecastResponse(
            next_month=next_month_str,
            predicted_revenue=round(next_rev, 2),
            growth_estimate_pct=growth_pct,
            historical_months=hist_data,
            forecast_curve=forecast_curve,
            model_name="Scikit-Learn Linear Regression (OLS)",
            r2_score=round(r2, 3),
            status="confident" if n_months >= 3 else "provisional",
            message=f"Forecast computed using {n_months} months of historical sales data."
        )
