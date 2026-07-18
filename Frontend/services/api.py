"""
API Service Layer — CognixOps Frontend
Handles all HTTP calls to the FastAPI backend and normalizes error handling.
"""

import requests
import streamlit as st
from config import API_BASE

_TIMEOUT = 15


# ── Error parsing ────────────────────────────────────────────────────────
def _friendly_message(response: requests.Response) -> str:
    """Backend returns {"status":"error","code":...,"message":...}; surface just the message."""
    try:
        body = response.json()
        if isinstance(body, dict) and body.get("message"):
            return body["message"]
    except ValueError:
        pass
    return response.text[:200] if response.text else f"HTTP {response.status_code}"


def _request(method: str, path: str, **kwargs) -> dict | None:
    url = f"{API_BASE}{path}"
    try:
        r = requests.request(method, url, timeout=_TIMEOUT, **kwargs)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error(f"Cannot reach the backend at {API_BASE}. Is it running?")
        return None
    except requests.exceptions.Timeout:
        st.error(f"Request to {path} timed out after {_TIMEOUT}s.")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"{_friendly_message(e.response)}")
        return None
    except Exception as e:
        st.error(f"Unexpected error calling {path}: {e}")
        return None


def _get(path: str, params: dict = None) -> dict | None:
    return _request("GET", path, params=params)


def _post(path: str, payload: dict) -> dict | None:
    return _request("POST", path, json=payload)


# ── Health ────────────────────────────────────────────────────────────────
def health_check() -> bool:
    try:
        r = requests.get(f"{API_BASE}/health", timeout=4)
        return r.status_code == 200
    except Exception:
        return False


# ── Forecast ─────────────────────────────────────────────────────────────
def get_forecast(sku: str, horizon_days: int = 7) -> dict | None:
    raw = _get("/forecast", {"sku": sku, "horizon": horizon_days})
    if raw is None:
        return None
    return {
        "sku": raw.get("sku"),
        "dates": raw.get("dates", []),
        "forecast": raw.get("forecast", []),
        "lower": raw.get("lower", []),
        "upper": raw.get("upper", []),
        "model_mae": raw.get("model_mae", 0),
        "baseline_mae": raw.get("baseline_mae", 0),
        "history_dates": raw.get("history_dates", []),
        "history_actuals": raw.get("history_actuals", []),
    }


def get_all_forecasts(skus: list[str], horizon_days: int = 7) -> list[dict]:
    return [d for sku in skus if (d := get_forecast(sku, horizon_days))]


# ── KPI ──────────────────────────────────────────────────────────────────
def get_kpis() -> dict | None:
    raw = _get("/kpi")
    if raw is None:
        return None
    return {
        "service_level": raw.get("service_level", 0),
        "total_cost": raw.get("total_cost", 0),
        "co2_kg": raw.get("co2_kg", 0),
        "on_time_delivery": raw.get("on_time_delivery", 0),
        "inventory_turnover": raw.get("inventory_turnover", 0),
    }


# ── Optimization ─────────────────────────────────────────────────────────
def get_optimization(disruption_type: str = "none") -> dict | None:
    raw = _post("/optimize", {"disruption_type": disruption_type})
    if raw is None:
        return None
    return {
        "routes": raw.get("routes", []),
        "total_cost": raw.get("total_cost", 0),
        "total_co2": raw.get("total_co2", 0),
        "service_level": raw.get("service_level", 0),
    }


# ── Simulation ───────────────────────────────────────────────────────────
def get_simulation(disruption_type: str) -> dict | None:
    if disruption_type == "none":
        return None

    raw = _post("/simulate", {"disruption_type": disruption_type})
    if raw is None:
        return None

    return {
        "kpi_before": raw.get("kpi_before", {}),
        "kpi_after": raw.get("kpi_after", {}),
        "recommended_actions": raw.get("recommended_actions", []),
        "severity": raw.get("severity", "low"),
        "risk_score": raw.get("risk_score", 0),
        "cost_impact": raw.get("cost_impact", 0),
        "delay_days": raw.get("delay_days", 0),
        "service_drop": raw.get("service_drop", 0),
        "new_routes": raw.get("new_routes", []),
    }


# ── Anomaly Detection ────────────────────────────────────────────────────
def get_anomalies(sku: str, sensitivity: float = 2.0) -> dict | None:
    return _post("/anomaly", {"product_id": sku, "sensitivity": sensitivity})
