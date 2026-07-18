"""
AI Logistics Optimization System — API entrypoint.

Architecture:
  app/core/      cross-cutting concerns (config, logging, exceptions, middleware)
  app/routes/    thin HTTP layer — request/response only, no business logic
  app/services/  business logic — forecasting, optimization, simulation, etc.
  app/models/    Pydantic schemas + enums (the API contract)
  app/utils/     data generation / loading helpers
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.core.exceptions import register_exception_handlers
from app.core.middleware import RequestContextMiddleware
from app.routes import forecast, optimize, simulate, kpi, anomaly, coordination
from app.models.schemas import HealthResponse
from app.utils.preprocessing import ensure_data

settings = get_settings()
configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s v%s (env=%s)", settings.app_name, settings.app_version, settings.environment)
    ensure_data()
    logger.info("Startup complete")
    yield
    logger.info("Shutting down")


app = FastAPI(
    title=settings.app_name,
    description="Predict demand, optimize routes, and simulate disruptions across a logistics network.",
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
)

# -----------------------------
# Middleware
# -----------------------------
app.add_middleware(RequestContextMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=settings.allowed_origins != ["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer-when-downgrade"
    return response


# -----------------------------
# Exception handling
# -----------------------------
register_exception_handlers(app)

# -----------------------------
# Root + Health
# -----------------------------
@app.get("/")
def root():
    return {"message": f"{settings.app_name} is running", "version": settings.app_version}


@app.get("/health", response_model=HealthResponse)
def health():
    return {"status": "ok", "message": "Backend is running"}


# -----------------------------
# Routes
# -----------------------------
app.include_router(forecast.router, prefix="/forecast", tags=["Forecast"])
app.include_router(optimize.router, prefix="/optimize", tags=["Optimization"])
app.include_router(simulate.router, prefix="/simulate", tags=["Simulation"])
app.include_router(kpi.router, prefix="/kpi", tags=["KPI"])
app.include_router(anomaly.router, prefix="/anomaly", tags=["Anomaly Detection"])
app.include_router(coordination.router, prefix="/coordination", tags=["Coordination"])
