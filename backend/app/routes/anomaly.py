from fastapi import APIRouter
from pydantic import BaseModel, Field, field_validator

from app.core.exceptions import NotFoundError
from app.core.logging import get_logger, Timer
from app.core_config import SKUS
from app.models.schemas import AnomalyResponse
from app.services.anomalies import run_anomaly_detection

router = APIRouter()
logger = get_logger(__name__)


class AnomalyRequest(BaseModel):
    product_id: str = Field(..., description="SKU to analyze", min_length=1, max_length=32)
    sensitivity: float = Field(2.0, ge=1.0, le=4.0, description="Z-score threshold")

    @field_validator("product_id")
    @classmethod
    def normalize_product_id(cls, v: str) -> str:
        return v.strip().upper()


@router.post("/", response_model=AnomalyResponse, summary="Detect demand anomalies for a SKU")
def detect_anomalies(request: AnomalyRequest):
    if request.product_id not in SKUS:
        raise NotFoundError(f"Unknown SKU '{request.product_id}'.", details={"valid_skus": SKUS})

    with Timer() as t:
        anomalies = run_anomaly_detection(request.product_id, request.sensitivity)
    logger.info("anomaly sku=%s sensitivity=%s found=%s took=%sms",
                request.product_id, request.sensitivity, len(anomalies), t.elapsed_ms)

    return {
        "status": "success",
        "sku": request.product_id,
        "sensitivity": request.sensitivity,
        "anomalies": anomalies,
    }
