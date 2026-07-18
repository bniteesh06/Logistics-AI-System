"""
Synthetic data generation + cached loaders.

Data is generated once at startup and is immutable for the life of the
process, so loaders are memoized with lru_cache to avoid re-reading CSVs
from disk on every request.
"""
import os
from functools import lru_cache

import numpy as np
import pandas as pd

from app.core.config import get_settings
from app.core.logging import get_logger
from app.core_config import SKUS

logger = get_logger(__name__)
settings = get_settings()

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def generate_data() -> None:
    os.makedirs(DATA_PATH, exist_ok=True)
    rng = np.random.default_rng(settings.data_seed)
    n_days = settings.history_days

    dates = pd.date_range(end=pd.Timestamp.today().normalize(), periods=n_days)

    # ── Demand history: trend + weekly seasonality + noise, per SKU ────────
    rows = []
    for i, sku in enumerate(SKUS):
        base = 80 + i * 15
        trend = np.linspace(0, 25 + i * 5, n_days)
        weekly = 12 * np.sin(2 * np.pi * np.arange(n_days) / 7)
        noise = rng.normal(0, 6, n_days)
        demand = np.clip(base + trend + weekly + noise, 5, None)

        anomaly_idx = rng.choice(n_days, size=3, replace=False)
        demand[anomaly_idx] += rng.choice([-1, 1], size=3) * rng.uniform(35, 55, size=3)

        rows.append(pd.DataFrame({"date": dates, "sku": sku, "demand": np.round(demand, 1)}))

    pd.concat(rows, ignore_index=True).to_csv(f"{DATA_PATH}/demand_history.csv", index=False)

    # ── Shipments (feeds on-time delivery + service level KPIs) ────────────
    n_ship = 400
    pd.DataFrame({
        "shipment_id": range(n_ship),
        "sku": rng.choice(SKUS, n_ship),
        "on_time": rng.choice([0, 1], n_ship, p=[0.09, 0.91]),
        "lead_time_days": np.round(rng.uniform(1.5, 6.5, n_ship), 1),
    }).to_csv(f"{DATA_PATH}/shipments.csv", index=False)

    # ── Inventory (feeds inventory turnover) ────────────────────────────────
    pd.DataFrame({
        "sku": SKUS,
        "stock": rng.integers(60, 260, len(SKUS)),
        "reorder_point": rng.integers(40, 90, len(SKUS)),
        "annual_units_sold": rng.integers(3_000, 9_000, len(SKUS)),
    }).to_csv(f"{DATA_PATH}/inventory.csv", index=False)

    logger.info("Generated demand_history/shipments/inventory (%s days, seed=%s) -> %s",
                n_days, settings.data_seed, DATA_PATH)


@lru_cache
def load_demand_history() -> pd.DataFrame:
    path = f"{DATA_PATH}/demand_history.csv"
    if not os.path.exists(path):
        generate_data()
    return pd.read_csv(path, parse_dates=["date"])


@lru_cache
def load_shipments() -> pd.DataFrame:
    path = f"{DATA_PATH}/shipments.csv"
    if not os.path.exists(path):
        generate_data()
    return pd.read_csv(path)


@lru_cache
def load_inventory() -> pd.DataFrame:
    path = f"{DATA_PATH}/inventory.csv"
    if not os.path.exists(path):
        generate_data()
    return pd.read_csv(path)
