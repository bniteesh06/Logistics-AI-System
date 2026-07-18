from app.services.kpi import calculate_kpis
from app.services.optimization import run_optimization

DISRUPTION_PROFILES = {
    "none": dict(
        severity="low", risk_score=0.10, delay_days=0.0, cost_impact_pct=0.0,
        actions=["No active disruption — network is operating at baseline."],
    ),
    "port_closure": dict(
        severity="high", risk_score=0.78, delay_days=3.5, cost_impact_pct=0.14,
        actions=[
            "Reroute London-origin volume through the Amsterdam plant for the next 5 days",
            "Notify the Munich customer of a 2-3 day delay on affected SKUs",
            "Pre-book air-freight capacity as a contingency for priority orders",
            "Escalate to the carrier for an updated port-reopening ETA",
        ],
    ),
    "supplier_delay": dict(
        severity="medium", risk_score=0.52, delay_days=2.0, cost_impact_pct=0.08,
        actions=[
            "Pull forward safety stock at the Manchester plant to cover the gap",
            "Split orders across the Amsterdam plant to reduce single-source risk",
            "Flag affected SKUs for tighter reorder-point monitoring",
        ],
    ),
    "weather": dict(
        severity="medium", risk_score=0.45, delay_days=1.5, cost_impact_pct=0.10,
        actions=[
            "Shift routing toward inland warehouse-origin lanes where possible",
            "Add buffer time to customer delivery promises for the next 48 hours",
            "Re-run this simulation every 6 hours as the forecast updates",
        ],
    ),
    "demand_spike": dict(
        severity="medium", risk_score=0.40, delay_days=1.0, cost_impact_pct=0.09,
        actions=[
            "Raise the safety-stock threshold for the affected SKU",
            "Activate secondary supplier capacity for the short term",
            "Prioritize existing contracted customers over spot orders",
        ],
    ),
    "transport_failure": dict(
        severity="critical", risk_score=0.85, delay_days=4.0, cost_impact_pct=0.18,
        actions=[
            "Immediately reroute all in-transit orders via the next-best carrier",
            "Activate the backup carrier contract for the affected lane",
            "Notify customer success to proactively contact impacted accounts",
            "Open an incident ticket and assign a logistics on-call lead",
        ],
    ),
}


def run_simulation(disruption_type: str) -> dict:
    profile = DISRUPTION_PROFILES.get(disruption_type, DISRUPTION_PROFILES["none"])

    kpi_before = calculate_kpis()
    opt_before = run_optimization("none")
    opt_after = run_optimization(disruption_type)

    cost_impact_pct = profile["cost_impact_pct"]
    service_drop = round(opt_before["service_level"] - opt_after["service_level"], 1)

    kpi_after = {
        "service_level": opt_after["service_level"],
        "total_cost": round(kpi_before["total_cost"] * (1 + cost_impact_pct), 2),
        "co2_kg": round(kpi_before["co2_kg"] * (1 + cost_impact_pct * 0.6), 2),
        "on_time_delivery": round(max(kpi_before["on_time_delivery"] - service_drop * 1.3, 0), 1),
    }

    return {
        "kpi_before": {
            "service_level": kpi_before["service_level"],
            "total_cost": kpi_before["total_cost"],
            "co2_kg": kpi_before["co2_kg"],
            "on_time_delivery": kpi_before["on_time_delivery"],
        },
        "kpi_after": kpi_after,
        "recommended_actions": profile["actions"],
        "severity": profile["severity"],
        "risk_score": profile["risk_score"],
        "cost_impact": round(kpi_after["total_cost"] - kpi_before["total_cost"], 2),
        "delay_days": profile["delay_days"],
        "service_drop": service_drop,
        "new_routes": opt_after["routes"],
    }
