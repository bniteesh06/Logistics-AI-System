from fastapi import APIRouter

from app.core.logging import get_logger, Timer
from app.models.schemas import CoordinationNetworkResponse, CoordinationFeedResponse
from app.services.coordination import get_network, get_feed

router = APIRouter()
logger = get_logger(__name__)


@router.get("/network", response_model=CoordinationNetworkResponse, summary="Get the supplier/factory/customer network")
def coordination_network():
    with Timer() as t:
        data = get_network()
    logger.info("coordination_network took=%sms", t.elapsed_ms)
    return {"status": "success", **data}


@router.get("/feed", response_model=CoordinationFeedResponse, summary="Get the live coordination event feed")
def coordination_feed():
    return {"status": "success", **get_feed()}
