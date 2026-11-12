from fastapi import APIRouter, Depends
from backend.api.schemas import StatisticsOut, RadiusSummaryOut
from backend.services.exoplanet_service import ExoplanetService
from backend.api.dependencies import get_service

router = APIRouter(prefix="/statistics", tags=["statistics"])

@router.get("", response_model=StatisticsOut)
def get_statistics(service: ExoplanetService = Depends(get_service)):
    stats = service.get_statistics()
    return StatisticsOut(
        total_planets=stats.total_planets,
        radius=RadiusSummaryOut.model_validate(stats.radius) if stats.radius is not None else None,
        category_counts={category.value: n for category, n in stats.category_counts.items()},
    )