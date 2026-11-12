import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.models.planet import Planet, PlanetCategory
from backend.services.exoplanet_service import ExoplanetService, InvalidQueryError


class FakeRepository:
    def __init__(self, planets):
        self._planets = planets

    def get_all_planets(self):
        return self._planets


def make_planet(radius=None, period=None, mass=None, year=2020):
    return Planet(planet_id=1, name="Test", star_id=1, discovery_method="Transit",
                  discovery_year=year, mass_provenance="Mass",
                  radius_earth=radius, orbital_period_days=period, mass_earth=mass)


def service_with(planets):
    return ExoplanetService(FakeRepository(planets))


# ---------- Unit tests (no database) ----------

def test_histogram_counts_only_known_values():
    bins = service_with([make_planet(radius=0.5), make_planet(radius=3.0), make_planet()]).histogram("radius")
    assert sum(b.count for b in bins) == 2


def test_histogram_value_on_an_edge_goes_into_the_upper_bin():
    bins = service_with([make_planet(radius=1.0)]).histogram("radius")
    filled = [b for b in bins if b.count == 1]
    assert len(filled) == 1
    assert filled[0].low == 1.0


def test_histogram_bins_are_contiguous():
    bins = service_with([]).histogram("mass")
    for current, following in zip(bins, bins[1:]):
        assert current.high == following.low


def test_histogram_unknown_metric_raises():
    with pytest.raises(InvalidQueryError):
        service_with([]).histogram("colour")


def test_scatter_includes_only_planets_with_both_values():
    planets = [make_planet(radius=1.0, period=10.0), make_planet(radius=1.0), make_planet(period=10.0)]
    points = service_with(planets).radius_period_points()
    assert len(points) == 1
    assert points[0].category == PlanetCategory.EARTH_LIKE


def test_discoveries_fill_years_with_none():
    planets = [make_planet(year=2000), make_planet(year=2002), make_planet(year=2002)]
    result = service_with(planets).discoveries_per_year()
    assert [(y.year, y.count) for y in result] == [(2000, 1), (2001, 0), (2002, 2)]


def test_discoveries_with_no_planets_is_empty():
    assert service_with([]).discoveries_per_year() == []


# ---------- API tests (use the real database; snapshots of the 2026-10-31 data) ----------

client = TestClient(app)


def test_histogram_endpoint_counts_match_known_values():
    for metric, known in [("radius", 6401), ("mass", 6421), ("period", 6097)]:
        bins = client.get("/insights/histogram", params={"metric": metric}).json()
        assert sum(b["count"] for b in bins) == known


def test_histogram_defaults_to_radius():
    body = client.get("/insights/histogram").json()
    assert sum(b["count"] for b in body) == 6401


def test_histogram_bad_metric_is_422():
    response = client.get("/insights/histogram", params={"metric": "colour"})
    assert response.status_code == 422
    assert "Unknown metric" in response.json()["detail"]


def test_scatter_endpoint_points_have_both_values():
    points = client.get("/insights/radius-period").json()
    assert len(points) == 6050
    assert all(p["radius_earth"] > 0 and p["orbital_period_days"] > 0 for p in points)


def test_discoveries_endpoint_is_continuous_and_complete():
    rows = client.get("/insights/discoveries").json()
    years = [r["year"] for r in rows]
    assert years == list(range(years[0], years[-1] + 1))
    assert sum(r["count"] for r in rows) == 6451