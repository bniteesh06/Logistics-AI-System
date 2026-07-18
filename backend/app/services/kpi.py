from app.utils.data_generator import load_shipments, load_inventory, load_demand_history
from app.services.optimization import run_optimization


def calculate_kpis() -> dict:
    shipments = load_shipments()
    inventory = load_inventory()
    demand = load_demand_history()

    on_time_delivery = round(float(shipments["on_time"].mean() * 100), 1)
    lead_time_std = float(shipments["lead_time_days"].std())
    service_level = round(min(99.5, max(0.0, on_time_delivery - lead_time_std * 1.2)), 1)

    turnover_ratio = inventory["annual_units_sold"] / inventory["stock"]
    inventory_turnover = round(float(turnover_ratio.mean()), 2)

    baseline = run_optimization("none")
    avg_daily_units = float(demand.groupby("date")["demand"].sum().mean())
    total_cost = round(baseline["total_cost"] * avg_daily_units / 10.0, 2)
    co2_kg = round(baseline["total_co2"] * avg_daily_units / 10.0, 2)

    return {
        "service_level": service_level,
        "total_cost": total_cost,
        "co2_kg": co2_kg,
        "on_time_delivery": on_time_delivery,
        "inventory_turnover": inventory_turnover,
    }
