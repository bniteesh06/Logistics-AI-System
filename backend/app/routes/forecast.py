from fastapi import APIRouter, Query

from app.core.config import get_settings
from app.core.exceptions import NotFoundError, InsufficientDataError
from app.core.logging import get_logger, Timer
from app.core_config import SKUS
from app.models.schemas import ForecastResponse
from app.services.forecasting import run_forecast

router = APIRouter()
logger = get_logger(__name__)
settings = get_settings()


@router.get("/", response_model=ForecastResponse, summary="Get demand forecast for a SKU")
def get_forecast(
    sku: str = Query(SKUS[0], description="SKU identifier"),
    horizon: int = Query(7, ge=settings.min_forecast_horizon, le=settings.max_forecast_horizon,
                          description="Days to forecast forward"),
):
    sku = sku.strip().upper()
    if sku not in SKUS:
        raise NotFoundError(f"Unknown SKU '{sku}'.", details={"valid_skus": SKUS})

    with Timer() as t:
        try:
            result = run_forecast(sku, horizon)
        except ValueError as e:
            raise InsufficientDataError(str(e))
    logger.info("forecast sku=%s horizon=%s took=%sms", sku, horizon, t.elapsed_ms)

    return {"status": "success", **result}
