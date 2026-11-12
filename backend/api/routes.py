from fastapi import APIRouter, Depends, Query
from typing import Optional
from backend.api.schemas import PlanetOut, PlanetPage, CompareOut, CompareRequest
from backend.api.dependencies import get_service
from backend.services.exoplanet_service import ExoplanetService

router = APIRouter(prefix="/planets", tags=["planets"])

@router.get("/search", response_model=PlanetPage)
def search_planets(
    q: Optional[str] = Query(None, min_length=1, max_length=100),
    min_radius: Optional[float] = Query(None, ge=0),
    max_radius: Optional[float] = Query(None, ge=0),
    hostname: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    service: ExoplanetService = Depends(get_service),
):

    planets, total = service.search_planets(q, min_radius, max_radius, hostname, limit, offset)

    return PlanetPage(
        total=total,
        limit=limit,
        offset=offset,
        items=[PlanetOut.model_validate(p) for p in planets],
    ) 
    
@router.get("", response_model=PlanetPage)
def list_planets(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    service: ExoplanetService = Depends(get_service),
):
    planets, total = service.list_planets(limit, offset) 
    return PlanetPage(
        total=total,
        limit=limit,
        offset=offset,
        items= [PlanetOut.model_validate(p) for p in planets]
    )

@router.get("/largest", response_model=PlanetOut)
def get_largest_planet(service: ExoplanetService = Depends(get_service)):
    largest_planet = service.get_largest_planet()
    return PlanetOut.model_validate(largest_planet)

@router.post("/compare", response_model=CompareOut)
def compare_planets(
    request: CompareRequest,
    service: ExoplanetService = Depends(get_service),
):
    planets = service.compare_planets(request.names)
    return CompareOut(planets=[PlanetOut.model_validate(p) for p in planets])


@router.get("/{name}", response_model=PlanetOut)
def get_planet(name: str, service: ExoplanetService = Depends(get_service)):

    planet = service.get_planet(name)
    return PlanetOut.model_validate(planet)
