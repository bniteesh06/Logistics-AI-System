"""
Lightweight forecasting: linear trend + day-of-week seasonality, fit with
numpy. Not Prophet/XGBoost-grade, but genuinely fit to the generated demand
history (not hardcoded) and backtested against a naive baseline so model_mae
vs baseline_mae is a real, meaningful comparison.
"""

import numpy as np
import pandas as pd

from app.utils.data_generator import load_demand_history

HOLDOUT_DAYS = 14
HISTORY_CONTEXT_DAYS = 21


def _fit(df: pd.DataFrame):
    idx = np.arange(len(df))
    weekday = df["date"].dt.dayofweek.values
    y = df["demand"].values

    coeffs = np.polyfit(idx, y, 1)
    trend = np.polyval(coeffs, idx)
    resid = y - trend

    seasonal = {}
    for wd in range(7):
        mask = weekday == wd
        seasonal[wd] = float(resid[mask].mean()) if mask.any() else 0.0

    fitted = trend + np.array([seasonal[wd] for wd in weekday])
    resid_std = float((y - fitted).std())
    return coeffs, seasonal, resid_std


def _predict(coeffs, seasonal, start_idx, n, start_weekday):
    idx = np.arange(start_idx, start_idx + n)
    trend = np.polyval(coeffs, idx)
    weekdays = [(start_weekday + i) % 7 for i in range(n)]
    seasonal_component = np.array([seasonal[wd] for wd in weekdays])
    return np.clip(trend + seasonal_component, 0, None)


def _mae(a, b) -> float:
    return float(np.mean(np.abs(np.array(a) - np.array(b))))


def run_forecast(sku: str, horizon: int = 7) -> dict:
    df = load_demand_history()
    df = df[df["sku"] == sku].sort_values("date").reset_index(drop=True)

    if df.empty:
        raise ValueError(f"Unknown SKU: {sku}")
    if len(df) < HOLDOUT_DAYS + 10:
        raise ValueError(f"Not enough history for {sku} to backtest")

    # ── Backtest: hold out the last HOLDOUT_DAYS to compare model vs naive ──
    train, test = df.iloc[:-HOLDOUT_DAYS], df.iloc[-HOLDOUT_DAYS:]
    coeffs, seasonal, _ = _fit(train)
    bt_start_weekday = int((train["date"].dt.dayofweek.iloc[-1] + 1) % 7)
    bt_pred = _predict(coeffs, seasonal, len(train), HOLDOUT_DAYS, bt_start_weekday)
    naive_pred = np.repeat(train["demand"].iloc[-1], HOLDOUT_DAYS)

    model_mae = _mae(bt_pred, test["demand"].values)
    baseline_mae = _mae(naive_pred, test["demand"].values)

    # ── Refit on full history, project `horizon` days forward ─────────────
    coeffs, seasonal, resid_std = _fit(df)
    start_weekday = int((df["date"].dt.dayofweek.iloc[-1] + 1) % 7)
    forecast = _predict(coeffs, seasonal, len(df), horizon, start_weekday)
    future_dates = pd.date_range(df["date"].iloc[-1] + pd.Timedelta(days=1), periods=horizon)

    z = 1.28  # ~80% interval
    lower = np.clip(forecast - z * resid_std, 0, None)
    upper = forecast + z * resid_std

    # Trailing window of actuals so the chart can show history flowing into the forecast
    history_window = df.tail(HISTORY_CONTEXT_DAYS)

    return {
        "sku": sku,
        "dates": [d.strftime("%Y-%m-%d") for d in future_dates],
        "forecast": [round(v, 1) for v in forecast.tolist()],
        "lower": [round(v, 1) for v in lower.tolist()],
        "upper": [round(v, 1) for v in upper.tolist()],
        "model_mae": round(model_mae, 2),
        "baseline_mae": round(baseline_mae, 2),
        "history_dates": [d.strftime("%Y-%m-%d") for d in history_window["date"]],
        "history_actuals": [round(v, 1) for v in history_window["demand"].tolist()],
    }
