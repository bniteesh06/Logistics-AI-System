from enum import Enum


class DisruptionType(str, Enum):
    """Must match Frontend/config.py DISRUPTION_OPTIONS keys exactly."""
    none = "none"
    port_closure = "port_closure"
    supplier_delay = "supplier_delay"
    weather = "weather"
    demand_spike = "demand_spike"
    transport_failure = "transport_failure"


class SeverityLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"
