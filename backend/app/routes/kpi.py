from fastapi import APIRouter

from app.core.logging import get_logger, Timer
from app.models.schemas import KPIResponse
from app.services.kpi import calculate_kpis

router = APIRouter()
logger = get_logger(__name__)


@router.get("/", response_model=KPIResponse, summary="Get current network KPIs")
def get_kpis():
    with Timer() as t:
        result = calculate_kpis()
    logger.info("kpi took=%sms", t.elapsed_ms)
    return {"status": "success", **result}
