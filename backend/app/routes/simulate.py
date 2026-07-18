from fastapi import APIRouter

from app.core.logging import get_logger, Timer
from app.models.schemas import SimulationRequest, SimulationResponse
from app.services.simulation import run_simulation

router = APIRouter()
logger = get_logger(__name__)


@router.post("/", response_model=SimulationResponse, summary="Simulate a disruption scenario")
def simulate(request: SimulationRequest):
    with Timer() as t:
        result = run_simulation(request.disruption_type.value)
    logger.info("simulate disruption=%s severity=%s took=%sms",
                request.disruption_type.value, result["severity"], t.elapsed_ms)
    return {"status": "success", "scenario": request.disruption_type.value, **result}
