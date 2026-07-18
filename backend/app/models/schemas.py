from pydantic import BaseModel, Field
from typing import List, Dict, Optional

from app.models.enums import DisruptionType, SeverityLevel


class BaseResponse(BaseModel):
    status: str = "success"
    message: Optional[str] = None


# ── Forecasting ──────────────────────────────────────────────────────────
class ForecastResponse(BaseResponse):
    sku: str
    dates: List[str]
    forecast: List[float]
    lower: List[float]
    upper: List[float]
    model_mae: float
    baseline_mae: float
    history_dates: List[str] = []
    history_actuals: List[float] = []


# ── Optimization ─────────────────────────────────────────────────────────
class RouteEdge(BaseModel):
    name: str
    from_node: str
    to_node: str
    distance_km: float
    cost: float
    co2: float
    selected: bool
    disrupted: bool


class OptimizationResponse(BaseResponse):
    routes: List[RouteEdge]
    total_cost: float
    total_co2: float
    service_level: float


# ── Simulation ───────────────────────────────────────────────────────────
class SimulationRequest(BaseModel):
    disruption_type: DisruptionType = Field(..., description="Type of disruption to simulate")


class KpiSnapshot(BaseModel):
    service_level: float
    total_cost: float
    co2_kg: float
    on_time_delivery: float


class SimulationResponse(BaseResponse):
    scenario: str
    kpi_before: KpiSnapshot
    kpi_after: KpiSnapshot
    recommended_actions: List[str]
    severity: SeverityLevel
    risk_score: float
    cost_impact: float
    delay_days: float
    service_drop: float
    new_routes: List[RouteEdge]


# ── KPI ──────────────────────────────────────────────────────────────────
class KPIResponse(BaseResponse):
    service_level: float
    total_cost: float
    co2_kg: float
    on_time_delivery: float
    inventory_turnover: float


# ── Anomaly detection ────────────────────────────────────────────────────
class AnomalyPoint(BaseModel):
    date: str
    demand: float
    z_score: float


class AnomalyResponse(BaseResponse):
    sku: str
    sensitivity: float
    anomalies: List[AnomalyPoint]


# ── Coordination hub ─────────────────────────────────────────────────────
class SupplierNode(BaseModel):
    name: str
    location: str
    lat: float
    lon: float
    status: str
    label: str
    stock_units: int
    lead_time_days: int
    capacity_units: int
    contact: str


class FactoryNode(BaseModel):
    name: str
    location: str
    lat: float
    lon: float
    status: str
    label: str
    output_per_day: int
    utilization: float
    queue_days: int
    capacity_units: int


class CustomerNode(BaseModel):
    name: str
    location: str
    lat: float
    lon: float
    status: str
    label: str
    units_needed: int
    eta_days: int
    contract_units_month: int
    priority: str


class OrderFlow(BaseModel):
    id: str
    supplier: str
    factory: str
    customer: str
    units: int
    status: str


class CoordinationNetworkResponse(BaseResponse):
    suppliers: Dict[str, SupplierNode]
    factories: Dict[str, FactoryNode]
    customers: Dict[str, CustomerNode]
    order_flows: List[OrderFlow]


class FeedEvent(BaseModel):
    title: str
    body: str
    severity: str
    minutes_ago: int


class CoordinationFeedResponse(BaseResponse):
    events: List[FeedEvent]


# ── Health ───────────────────────────────────────────────────────────────
class HealthResponse(BaseModel):
    status: str = "ok"
    message: str = "Backend is running"
