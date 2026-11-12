import pytest
from backend.models.planet import Planet, PlanetCategory

def make_planet(radius):
        return Planet(
        planet_id=1,
        name="Test A",
        star_id=1,
        discovery_method="Transit",
        discovery_year=2020,
        mass_provenance="Mass",
        radius_earth=radius)

@pytest.mark.parametrize("radius, expected", [
    (None, PlanetCategory.UNKNOWN),
    (1.0, PlanetCategory.EARTH_LIKE),
    # add the boundaries: 1.25, 2.0, 6.0, and a value just below each
])
def test_category(radius, expected):
    assert make_planet(radius).category == expected