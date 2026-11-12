from fastapi import Depends
from backend.repository.exoplanet_repository import ExoplanetRepository
from backend.services.exoplanet_service import ExoplanetService


def get_repository() -> ExoplanetRepository:
    return ExoplanetRepository()

def get_service(repo: ExoplanetRepository = Depends(get_repository)) -> ExoplanetService:
    return ExoplanetService(repo)
