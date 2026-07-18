from app.core_config import NODES, SOURCE_NODES, COST_PER_KM, CO2_PER_KM, HANDLING_FEE, haversine_km

BASE_SERVICE_LEVEL = 97.5


def _base_routes() -> list[dict]:
    routes = []
    for node_id in SOURCE_NODES:
        dist = haversine_km(node_id, "CUST")
        node_type = NODES[node_id]["type"]
        cost = dist * COST_PER_KM + HANDLING_FEE[node_type]
        co2 = dist * CO2_PER_KM
        routes.append({
            "name": f"{node_id} -> CUST",
            "from_node": node_id,
            "to_node": "CUST",
            "distance_km": round(dist, 1),
            "cost": round(cost, 2),
            "co2": round(co2, 2),
            "disrupted": False,
            "selected": False,
        })
    return routes


def run_optimization(disruption_type: str = "none") -> dict:
    routes = _base_routes()
    service_level = BASE_SERVICE_LEVEL

    # Which node would be cheapest under normal conditions (used by transport_failure)
    cheapest_node = min(routes, key=lambda r: r["cost"])["from_node"]

    if disruption_type == "port_closure":
        # WH-B (London) sits on the affected port lane
        for r in routes:
            if r["from_node"] == "WH-B":
                r["disrupted"] = True
        service_level -= 4.0

    elif disruption_type == "transport_failure":
        for r in routes:
            if r["from_node"] == cheapest_node:
                r["disrupted"] = True
        service_level -= 5.5

    elif disruption_type == "weather":
        for r in routes:
            r["cost"] = round(r["cost"] * 1.25, 2)
            r["co2"] = round(r["co2"] * 1.15, 2)
        service_level -= 2.5

    elif disruption_type == "supplier_delay":
        for r in routes:
            if NODES[r["from_node"]]["type"] == "plant":
                r["cost"] = round(r["cost"] * 1.20, 2)
        service_level -= 3.0

    elif disruption_type == "demand_spike":
        for r in routes:
            r["cost"] = round(r["cost"] * 1.15, 2)
        service_level -= 1.5

    viable = [r for r in routes if not r["disrupted"]]
    selected_node = min(viable, key=lambda r: r["cost"])["from_node"] if viable else None
    for r in routes:
        r["selected"] = r["from_node"] == selected_node

    selected_route = next((r for r in routes if r["selected"]), None)
    total_cost = selected_route["cost"] if selected_route else 0.0
    total_co2 = selected_route["co2"] if selected_route else 0.0

    return {
        "routes": routes,
        "total_cost": round(total_cost, 2),
        "total_co2": round(total_co2, 2),
        "service_level": round(max(service_level, 0), 1),
    }
