"""
Shared constants that MUST stay in sync with Frontend/config.py.
Kept in one place so backend routes/services never drift from what the UI expects.
"""

import math

# ── SKUs — must match Frontend/config.py SKUS ───────────────────────────────
SKUS = ["SKU-001", "SKU-002", "SKU-003", "SKU-004", "SKU-005"]

# ── Network nodes — must match Frontend/config.py NODES ─────────────────────
NODES = {
    "WH-A":  {"lat": 48.8566, "lon":  2.3522, "label": "Paris WH",        "type": "warehouse"},
    "WH-B":  {"lat": 51.5074, "lon": -0.1278, "label": "London WH",       "type": "warehouse"},
    "PLT-1": {"lat": 53.4808, "lon": -2.2426, "label": "Manchester Plant", "type": "plant"},
    "PLT-2": {"lat": 52.3667, "lon":  4.8945, "label": "Amsterdam Plant",  "type": "plant"},
    "CUST":  {"lat": 48.1351, "lon": 11.5820, "label": "Munich Customer",  "type": "customer"},
}

# Candidate source nodes that can fulfil the customer (everything but CUST itself)
SOURCE_NODES = [n for n in NODES if n != "CUST"]

# ── Cost model ────────────────────────────────────────────────────────────
COST_PER_KM = 1.35        # $/km
CO2_PER_KM = 0.62         # kg CO2/km (road freight avg)
HANDLING_FEE = {
    "warehouse": 18.0,
    "plant": 32.0,   # plants also do production changeover -> higher handling
}


def haversine_km(a: str, b: str) -> float:
    lat1, lon1 = NODES[a]["lat"], NODES[a]["lon"]
    lat2, lon2 = NODES[b]["lat"], NODES[b]["lon"]
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    x = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.asin(math.sqrt(x))
