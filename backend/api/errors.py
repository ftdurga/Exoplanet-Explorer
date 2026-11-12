import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from backend.database.connection import DatabaseConnectionError
from backend.repository.exoplanet_repository import PlanetNotFoundError, StarNotFoundError
from backend.services.exoplanet_service import InvalidQueryError

logger = logging.getLogger(__name__)


async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


async def invalid_query_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})


async def database_unavailable_handler(request: Request, exc: Exception) -> JSONResponse:
    # The real reason (host, database name) goes to the server log only.
    logger.error("Database unavailable: %s", exc)
    return JSONResponse(status_code=503,
                        content={"detail": "Database temporarily unavailable"})


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(PlanetNotFoundError, not_found_handler)
    app.add_exception_handler(StarNotFoundError, not_found_handler)
    app.add_exception_handler(InvalidQueryError, invalid_query_handler)
    app.add_exception_handler(DatabaseConnectionError, database_unavailable_handler)