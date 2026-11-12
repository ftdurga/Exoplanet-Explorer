import pytest

from backend.models.planet import PlanetCategory
from backend.repository.exoplanet_repository import ExoplanetRepository


@pytest.fixture
def fake_row():
    """One row as the database would return it (a dictionary keyed by column name)."""
    return {
        "planet_id": 1, "pl_name": "Test Planet", "star_id": 7,
        "discoverymethod": "Transit", "disc_year": 2020, "pl_bmassprov": "Mass",
        "pl_rade": 1.5, "pl_bmasse": None, "pl_orbper": 10.0,
        "pl_orbsmax": 0.1, "pl_orbeccen": None, "pl_eqt": 300.0, "pl_insol": 1.2,
        "hostname": "Test Star", "st_teff": 5000.0, "st_rad": 0.9,
        "st_mass": 0.8, "st_met": None, "st_spectype": "K2", "sy_dist": 12.3,
    }


@pytest.fixture
def planet(fake_row):
    return ExoplanetRepository()._row_to_planet(fake_row)


def test_planet_fields_are_mapped_to_readable_names(planet):
    assert planet.planet_id == 1
    assert planet.name == "Test Planet"
    assert planet.discovery_method == "Transit"
    assert planet.discovery_year == 2020
    assert planet.mass_provenance == "Mass"
    assert planet.radius_earth == 1.5
    assert planet.orbital_period_days == 10.0
    assert planet.semi_major_axis_au == 0.1
    assert planet.equilibrium_temp_k == 300.0
    assert planet.insolation == 1.2


def test_star_fields_are_mapped_to_readable_names(planet):
    assert planet.star.hostname == "Test Star"
    assert planet.star.temperature_k == 5000.0
    assert planet.star.radius_solar == 0.9
    assert planet.star.mass_solar == 0.8
    assert planet.star.spectral_type == "K2"
    assert planet.star.distance_pc == 12.3


def test_planet_and_star_share_the_same_star_id(planet):
    assert planet.star_id == 7
    assert planet.star.star_id == 7


def test_null_values_stay_none(planet):
    assert planet.mass_earth is None
    assert planet.eccentricity is None
    assert planet.star.metallicity is None


def test_category_is_derived_from_mapped_radius(planet):
    assert planet.category == PlanetCategory.SUPER_EARTH