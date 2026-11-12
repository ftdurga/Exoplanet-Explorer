import pytest
from fastapi.testclient import TestClient

from backend.api.dependencies import get_repository
from backend.database.connection import DatabaseConnectionError
from backend.main import app
from backend.models.planet import Planet
from backend.repository.exoplanet_repository import PlanetNotFoundError


def make_planet(name, radius=1.0):
    return Planet(planet_id=1, name=name, star_id=1, discovery_method="Transit",
                  discovery_year=2020, mass_provenance="Mass", radius_earth=radius)


class FakeApiRepository:
    def __init__(self):
        self._planets = [make_planet("Alpha b", 0.5), make_planet("Beta b", 3.0),
                         make_planet("Gamma b", None)]

    def get_planet_by_name(self, name):
        for planet in self._planets:
            if planet.name == name:
                return planet
        raise PlanetNotFoundError(f"No planet named '{name}'")

    def get_all_planets(self):
        return self._planets

    def count_planets(self):
        return len(self._planets)

    def get_planets_page(self, limit, offset):
        return self._planets[offset:offset + limit]


class BrokenRepository:
    def get_planet_by_name(self, name):
        raise DatabaseConnectionError("Could not connect to secret-host/secret_db")


@pytest.fixture
def client():
    app.dependency_overrides[get_repository] = lambda: FakeApiRepository()
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_get_planet_from_fake_repository(client):
    body = client.get("/planets/Alpha b").json()
    assert body["name"] == "Alpha b"
    assert body["category"] == "Earth-like"


def test_unknown_planet_is_404(client):
    response = client.get("/planets/Nope")
    assert response.status_code == 404
    assert "Nope" in response.json()["detail"]


def test_list_uses_fake_data(client):
    body = client.get("/planets", params={"limit": 2}).json()
    assert body["total"] == 3
    assert [p["name"] for p in body["items"]] == ["Alpha b", "Beta b"]


def test_statistics_from_fake_data(client):
    body = client.get("/statistics").json()
    assert body["total_planets"] == 3
    assert body["radius"]["count"] == 2
    assert body["category_counts"]["Unknown"] == 1


def test_compare_with_fake_data(client):
    response = client.post("/planets/compare", json={"names": ["Beta b", "Alpha b"]})
    assert [p["name"] for p in response.json()["planets"]] == ["Beta b", "Alpha b"]


def test_compare_duplicates_is_422(client):
    response = client.post("/planets/compare", json={"names": ["Alpha b", "Alpha b"]})
    assert response.status_code == 422


def test_database_down_is_503_without_leaking_details():
    app.dependency_overrides[get_repository] = lambda: BrokenRepository()
    try:
        response = TestClient(app).get("/planets/Alpha b")
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 503
    assert "secret" not in response.text


def test_cors_allows_the_frontend_origin(client):
    response = client.get("/health", headers={"Origin": "http://localhost:5173"})
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_cors_does_not_allow_other_origins(client):
    response = client.get("/health", headers={"Origin": "http://evil.example"})
    assert "access-control-allow-origin" not in response.headers