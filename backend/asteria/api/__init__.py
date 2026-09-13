"""The HTTP surface. One router per dashboard screen (plan/DASHBOARD.md)."""

from fastapi import APIRouter

from asteria.api.routes import capture, fleet, indicators, ncs, signals

api_router = APIRouter()
api_router.include_router(capture.router, prefix="/capture", tags=["capture"])
api_router.include_router(fleet.router, prefix="/fleet", tags=["fleet"])
api_router.include_router(indicators.router, prefix="/indicators", tags=["indicators"])
api_router.include_router(signals.router, prefix="/signals", tags=["signals"])
api_router.include_router(ncs.router, prefix="/ncs", tags=["ncs"])
