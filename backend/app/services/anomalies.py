import numpy as np

from app.utils.data_generator import load_demand_history
from app.services.forecasting import _fit


def run_anomaly_detection(sku: str, sensitivity: float = 2.0) -> list[dict]:
    """Z-score anomaly detection against the trend+seasonal fit used for forecasting."""
    df = load_demand_history()
    df = df[df["sku"] == sku].sort_values("date").reset_index(drop=True)
    if df.empty:
        raise ValueError(f"Unknown SKU: {sku}")

    coeffs, seasonal, resid_std = _fit(df)
    idx = np.arange(len(df))
    weekday = df["date"].dt.dayofweek.values
    trend = np.polyval(coeffs, idx)
    seasonal_component = np.array([seasonal[wd] for wd in weekday])
    fitted = trend + seasonal_component
    residuals = df["demand"].values - fitted
    z_scores = residuals / (resid_std if resid_std > 0 else 1.0)

    anomalies = []
    for i, z in enumerate(z_scores):
        if abs(z) >= sensitivity:
            anomalies.append({
                "date": df["date"].iloc[i].strftime("%Y-%m-%d"),
                "demand": round(float(df["demand"].iloc[i]), 1),
                "z_score": round(float(z), 2),
            })
    return anomalies
