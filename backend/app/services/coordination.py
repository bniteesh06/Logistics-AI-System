"""Mock but internally-consistent supplier -> factory -> customer network."""

SUPPLIERS = {
    "SUP-1": dict(name="Shenzhen Components Co.", location="Shenzhen, CN", lat=22.5431, lon=114.0579,
                  status="ok", label="On schedule", stock_units=8400, lead_time_days=18,
                  capacity_units=12000, contact="wei.zhang@szc.example"),
    "SUP-2": dict(name="Rotterdam Raw Materials", location="Rotterdam, NL", lat=51.9244, lon=4.4777,
                  status="warning", label="Running below buffer stock", stock_units=2100, lead_time_days=4,
                  capacity_units=6000, contact="l.devries@rrm.example"),
    "SUP-3": dict(name="Milan Textile Group", location="Milan, IT", lat=45.4642, lon=9.1900,
                  status="ok", label="On schedule", stock_units=5300, lead_time_days=7,
                  capacity_units=8000, contact="g.conti@mtg.example"),
}

FACTORIES = {
    "FAC-1": dict(name="Manchester Plant", location="Manchester, UK", lat=53.4808, lon=-2.2426,
                  status="ok", label="Normal throughput", output_per_day=640, utilization=0.81,
                  queue_days=1, capacity_units=800),
    "FAC-2": dict(name="Amsterdam Plant", location="Amsterdam, NL", lat=52.3667, lon=4.8945,
                  status="critical", label="Line 2 down for maintenance", output_per_day=210,
                  utilization=0.97, queue_days=4, capacity_units=560),
}

CUSTOMERS = {
    "CUST-1": dict(name="Munich Retail Group", location="Munich, DE", lat=48.1351, lon=11.5820,
                   status="ok", label="Orders on track", units_needed=3200, eta_days=2,
                   contract_units_month=42000, priority="high"),
    "CUST-2": dict(name="Berlin Distribution Hub", location="Berlin, DE", lat=52.5200, lon=13.4050,
                   status="warning", label="ETA slipping", units_needed=1850, eta_days=5,
                   contract_units_month=21000, priority="medium"),
    "CUST-3": dict(name="Vienna Logistics Partner", location="Vienna, AT", lat=48.2082, lon=16.3738,
                   status="ok", label="Orders on track", units_needed=980, eta_days=3,
                   contract_units_month=9600, priority="low"),
}

ORDER_FLOWS = [
    dict(id="OF-1001", supplier="SUP-1", factory="FAC-1", customer="CUST-1", units=1200, status="in_transit"),
    dict(id="OF-1002", supplier="SUP-2", factory="FAC-2", customer="CUST-2", units=650, status="at_risk"),
    dict(id="OF-1003", supplier="SUP-3", factory="FAC-1", customer="CUST-3", units=430, status="confirmed"),
    dict(id="OF-1004", supplier="SUP-1", factory="FAC-2", customer="CUST-1", units=900, status="delayed"),
    dict(id="OF-1005", supplier="SUP-2", factory="FAC-1", customer="CUST-2", units=780, status="delivered"),
]

FEED_EVENTS = [
    dict(title="Line 2 maintenance flagged at Amsterdam Plant", body="Utilization at 97% — queue extended to 4 days.",
         severity="critical", minutes_ago=6),
    dict(title="Rotterdam Raw Materials below buffer stock", body="Stock at 2,100 units, below the 2,500 safety threshold.",
         severity="warning", minutes_ago=24),
    dict(title="OF-1002 marked at risk", body="Berlin Distribution Hub shipment delayed at customs.",
         severity="warning", minutes_ago=41),
    dict(title="OF-1005 delivered", body="780 units delivered to Berlin Distribution Hub ahead of schedule.",
         severity="ok", minutes_ago=95),
    dict(title="Shenzhen Components Co. confirmed capacity", body="12,000 unit capacity confirmed for next cycle.",
         severity="ok", minutes_ago=132),
]


def get_network() -> dict:
    return {
        "suppliers": SUPPLIERS,
        "factories": FACTORIES,
        "customers": CUSTOMERS,
        "order_flows": ORDER_FLOWS,
    }


def get_feed() -> dict:
    return {"events": FEED_EVENTS}
