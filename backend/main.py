from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.errors import register_error_handlers
from backend.api.routes import router as planet_router
from backend.api.star_routes import router as star_router
from backend.api.stats_routes import router as stats_router
from backend.api.insights_routes import router as insights_router

app = FastAPI(title="Exoplanet Explorer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

register_error_handlers(app)

app.include_router(planet_router)
app.include_router(star_router)
app.include_router(stats_router)
app.include_router(insights_router)


@app.get("/")
def home():
    return {"message": "Exoplanet Explorer API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}