import pytest
from backend.models.planet import Planet, PlanetCategory
from backend.repository.exoplanet_repository import ExoplanetRepository, PlanetNotFoundError
from backend.services.exoplanet_service import ExoplanetService


# ---------- Test helpers ----------

class FakeRepository:
    """Stands in for the real repository. Has only the method the service uses."""

    def __init__(self, planets):
        self._planets = planets

    def get_all_planets(self):
        return self._planets
    
    def count_planets(self):
        return len(self._planets)

class SpyRepository:
    """Records how the service calls it. Method signatures mirror the real repository."""

    def __init__(self):
        self.calls = []

    def get_stars_page(self, limit, offset, q=None):
        self.calls.append(("get_stars_page", limit, offset, q))
        return []

    def count_stars(self, q=None):
        self.calls.append(("count_stars", q))
        return 0

    def search_planets(self, q=None, min_radius=None, max_radius=None,
                       hostname=None, limit=50, offset=0):
        self.calls.append(("search_planets", q, min_radius, max_radius, hostname, limit, offset))
        return []

    def count_search(self, q=None, min_radius=None, max_radius=None, hostname=None):
        self.calls.append(("count_search", q, min_radius, max_radius, hostname))
        return 0

class NamedFakeRepository:
    """A fake repository holding planets with the given names."""

    def __init__(self, names):
        self._planets = {
            name: Planet(planet_id=i, name=name, star_id=1,
                         discovery_method="Transit", discovery_year=2020,
                         mass_provenance="Mass", radius_earth=1.0)
            for i, name in enumerate(names)
        }

    def get_planet_by_name(self, name):
        if name not in self._planets:
            raise PlanetNotFoundError(f"No planet named '{name}'")
        return self._planets[name]


def make_planet(radius):
    return Planet(
        planet_id=1,
        name="Test planet",
        star_id=1,
        discovery_method="Transit",
        discovery_year=2020,
        mass_provenance="Mass",
        radius_earth=radius,
    )


def make_service(radii):
    """Build a service whose 'database' is a list of planets with these radii."""
    planets = [make_planet(r) for r in radii]
    return ExoplanetService(FakeRepository(planets))


# ---------- Unit tests: average_radius (no database) ----------

def test_average_radius_ignores_none():
    assert make_service([1.0, 3.0, None]).average_radius() == 2.0


def test_average_radius_all_unknown_returns_none():
    assert make_service([None, None]).average_radius() is None


def test_average_radius_empty_list_returns_none():
    assert make_service([]).average_radius() is None


# ---------- Unit tests: category_counts (no database) ----------

def test_category_counts_one_of_each():
    counts = make_service([1.0, 1.5, 3.0, 10.0, None]).category_counts()
    assert counts[PlanetCategory.EARTH_LIKE] == 1
    assert counts[PlanetCategory.SUPER_EARTH] == 1
    assert counts[PlanetCategory.NEPTUNE_LIKE] == 1
    assert counts[PlanetCategory.GIANT] == 1
    assert counts[PlanetCategory.UNKNOWN] == 1


def test_category_counts_includes_empty_categories():
    counts = make_service([1.0]).category_counts()
    print(set(counts))# all five keys are present
    assert set(counts) == set(PlanetCategory)   
    assert counts[PlanetCategory.EARTH_LIKE] == 1
    assert counts[PlanetCategory.GIANT] == 0


def test_category_counts_add_up_to_number_of_planets():
    radii = [0.5, 1.25, 2.0, 6.0, None, None]
    counts = make_service(radii).category_counts()
    assert sum(counts.values()) == len(radii)


# ---------- Unit tests: radius_summary (no database) ----------

def test_radius_summary_values():
    summary = make_service([1.0, 2.0, 3.0, 10.0]).radius_summary()
    assert summary.count == 4
    assert summary.minimum == 1.0
    assert summary.maximum == 10.0
    assert summary.mean == 4.0
    assert summary.median == 2.5


def test_radius_summary_ignores_none():
    summary = make_service([1.0, None, 3.0]).radius_summary()
    assert summary.count == 2
    assert summary.mean == 2.0


def test_radius_summary_no_data_returns_none():
    assert make_service([]).radius_summary() is None
    assert make_service([None]).radius_summary() is None


def test_outlier_pulls_mean_above_median():
    summary = make_service([1.0, 2.0, 3.0, 100.0]).radius_summary()
    assert summary.mean > summary.median


# ---------- Integration tests (need MySQL running) ----------
# These are snapshots of the 2026-10-31 NASA download.
# If you reload newer data, update the numbers.

@pytest.fixture(scope="module")
def real_service():
    return ExoplanetService(ExoplanetRepository())


def test_real_summary(real_service):
    summary = real_service.radius_summary()
    assert summary.count == 6401
    assert summary.minimum == pytest.approx(0.3098)
    assert summary.maximum == pytest.approx(87.20586985)
    assert summary.mean == pytest.approx(5.8447, abs=0.001)
    assert summary.median == pytest.approx(2.86)


def test_real_average_matches_summary_mean(real_service):
    assert real_service.average_radius() == pytest.approx(real_service.radius_summary().mean)


def test_real_category_counts(real_service):
    counts = real_service.category_counts()
    assert counts[PlanetCategory.EARTH_LIKE] == 583
    assert counts[PlanetCategory.SUPER_EARTH] == 1212
    assert counts[PlanetCategory.NEPTUNE_LIKE] == 2442
    assert counts[PlanetCategory.GIANT] == 2164
    assert counts[PlanetCategory.UNKNOWN] == 50
    assert sum(counts.values()) == 6451

def test_list_stars_passes_arguments_in_the_right_order():
    spy = SpyRepository()
    stars, total = ExoplanetService(spy).list_stars(q="trap", limit=10, offset=20)
    assert ("get_stars_page", 10, 20, "trap") in spy.calls
    assert ("count_stars", "trap") in spy.calls
    assert (stars, total) == ([], 0)


def test_search_planets_passes_filters_in_the_right_order():
    spy = SpyRepository()
    ExoplanetService(spy).search_planets(
        q="a", min_radius=1, max_radius=2, hostname="h", limit=5, offset=10
    )
    assert ("search_planets", "a", 1, 2, "h", 5, 10) in spy.calls
    assert ("count_search", "a", 1, 2, "h") in spy.calls


def test_search_planets_reversed_range_raises_before_using_repository():
    service = ExoplanetService(object())     # any repository call would raise AttributeError
    with pytest.raises(ValueError):
        service.search_planets(min_radius=5, max_radius=1)


def test_search_planets_equal_bounds_are_allowed():
    ExoplanetService(SpyRepository()).search_planets(min_radius=2, max_radius=2)


def test_get_statistics_combines_total_radius_and_counts():
    stats = make_service([1.0, 3.0, None]).get_statistics()
    assert stats.total_planets == 3
    assert stats.radius.count == 2
    assert stats.radius.mean == 2.0
    assert stats.category_counts[PlanetCategory.UNKNOWN] == 1


def test_get_statistics_with_no_known_radii():
    stats = make_service([None]).get_statistics()
    assert stats.radius is None
    assert stats.total_planets == 1
    
def test_compare_planets_keeps_requested_order():
    service = ExoplanetService(NamedFakeRepository(["A b", "B b", "C b"]))
    planets = service.compare_planets(["C b", "A b"])
    assert [p.name for p in planets] == ["C b", "A b"]


def test_compare_planets_duplicates_raise_before_using_repository():
    service = ExoplanetService(object())       # any repository call would fail
    with pytest.raises(ValueError):
        service.compare_planets(["A b", "A b"])


def test_compare_planets_unknown_name_raises():
    service = ExoplanetService(NamedFakeRepository(["A b"]))
    with pytest.raises(PlanetNotFoundError):
        service.compare_planets(["A b", "Fake Planet"])