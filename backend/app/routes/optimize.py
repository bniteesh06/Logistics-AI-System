from fastapi import APIRouter

from app.core.logging import get_logger, Timer
from app.models.schemas import OptimizationResponse, SimulationRequest
from app.services.optimization import run_optimization

router = APIRouter()
logger = get_logger(__name__)


@router.post("/", response_model=OptimizationResponse, summary="Compute the optimal fulfilment route")
def optimize_routes(request: SimulationRequest):
    with Timer() as t:
        result = run_optimization(request.disruption_type.value)
    logger.info("optimize disruption=%s took=%sms", request.disruption_type.value, t.elapsed_ms)
    return {"status": "success", **result}
