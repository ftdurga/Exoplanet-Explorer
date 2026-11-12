from fastapi import APIRouter, Depends, Query

from backend.api.dependencies import get_service
from backend.api.schemas import HistogramBinOut, ScatterPointOut, YearCountOut
from backend.services.exoplanet_service import ExoplanetService

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("/histogram", response_model=list[HistogramBinOut])
def histogram(metric: str = Query("radius"), service: ExoplanetService = Depends(get_service)):
    return [HistogramBinOut.model_validate(b) for b in service.histogram(metric)]


@router.get("/radius-period", response_model=list[ScatterPointOut])
def radius_period(service: ExoplanetService = Depends(get_service)):
    return [ScatterPointOut.model_validate(p) for p in service.radius_period_points()]


@router.get("/discoveries", response_model=list[YearCountOut])
def discoveries(service: ExoplanetService = Depends(get_service)):
    return [YearCountOut.model_validate(y) for y in service.discoveries_per_year()]