"""Structured logging setup. Call configure_logging() once, at startup."""
import logging
import sys
import time
import uuid
from contextvars import ContextVar

from app.core.config import get_settings

_request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = _request_id_ctx.get()
        return True


def configure_logging() -> None:
    settings = get_settings()
    handler = logging.StreamHandler(sys.stdout)

    if settings.log_json:
        fmt = (
            '{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s",'
            '"request_id":"%(request_id)s","message":"%(message)s"}'
        )
    else:
        fmt = "%(asctime)s | %(levelname)-8s | %(name)s | req=%(request_id)s | %(message)s"

    handler.setFormatter(logging.Formatter(fmt))
    handler.addFilter(RequestIdFilter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(settings.log_level)

    # Keep third-party loggers quieter than our own app logs
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def new_request_id() -> str:
    rid = uuid.uuid4().hex[:12]
    _request_id_ctx.set(rid)
    return rid


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


class Timer:
    """Small context manager for timing blocks, used in perf-sensitive services."""

    def __enter__(self):
        self._start = time.perf_counter()
        return self

    def __exit__(self, *exc):
        self.elapsed_ms = round((time.perf_counter() - self._start) * 1000, 2)
