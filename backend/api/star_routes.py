from fastapi import APIRouter, Depends, HTTPException, Query
from backend.api.schemas import PlanetSummaryOut, StarDetailOut, StarOut, StarPage
from backend.repository.exoplanet_repository import StarNotFoundError
from backend.services.exoplanet_service import ExoplanetService
from backend.api.dependencies import get_service
from typing import Optional


router = APIRouter(prefix="/stars", tags=["stars"])

@router.get("", response_model=StarPage)
def list_stars(
    q: Optional[str] = Query(None, min_length=1, max_length=100),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    service: ExoplanetService = Depends(get_service),
):
    stars, total = service.list_stars(q, limit, offset)
    return StarPage(
        total=total,
        limit=limit,
        offset=offset,
        items=[StarOut.model_validate(s) for s in stars],
    )

@router.get("/{star_id}", response_model=StarDetailOut)
def get_star(star_id: int, service: ExoplanetService = Depends(get_service)):
    try:
        star, planets = service.get_star(star_id)
    except StarNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except TypeError as e:
        raise HTTPException(status_code=422, detail=str(e))
    
    return StarDetailOut(
        **StarOut.model_validate(star).model_dump(),
        planet_count=len(planets),
        planets=[PlanetSummaryOut.model_validate(p) for p in planets],
    )