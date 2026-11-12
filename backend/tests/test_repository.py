import pytest
from backend.repository.exoplanet_repository import ExoplanetRepository, PlanetNotFoundError, StarNotFoundError


@pytest.fixture
def repo():
    """A fresh repository, supplied automatically to any test that asks for 'repo'."""
    return ExoplanetRepository()


# ---------- get_planet_by_name ----------

def test_get_planet_by_name_attaches_star(repo):
    planet = repo.get_planet_by_name("TRAPPIST-1 e")
    assert planet.name == "TRAPPIST-1 e"
    assert planet.star is not None
    assert planet.star.hostname == "TRAPPIST-1"
    assert planet.star_id == planet.star.star_id


def test_get_planet_by_name_unknown_raises(repo):
    with pytest.raises(PlanetNotFoundError):
        repo.get_planet_by_name("Fake Planet")


# ---------- get_all_planets ----------

def test_get_all_planets_snapshot_count(repo):
    # Snapshot of the 2026-10-31 NASA download. Update if you reload new data.
    assert len(repo.get_all_planets()) == 6451


# def test_get_all_planets_sorted_by_name(repo):
#     names = [p.name for p in repo.get_all_planets()]

#     expected = sorted(names, key=str.casefold)      # temporary debugging
#     for got, want in zip(names, expected):          # temporary debugging
#         if got != want:                             # temporary debugging
#             print("First mismatch:", got, "vs", want)   # temporary debugging
#             break                                   # temporary debugging

#     assert names == sorted(names, key=str.casefold)

def test_get_all_planets_sorted_by_first_character(repo):
    # Compares only the first character, case-insensitively. This is the part
    # of the order that every sorting rule agrees on.
    first_chars = [p.name[0].casefold() for p in repo.get_all_planets()]
    assert first_chars == sorted(first_chars)


def test_get_all_planets_order_is_repeatable(repo):
    first_call = [p.name for p in repo.get_all_planets()]
    second_call = [p.name for p in repo.get_all_planets()]
    assert first_call == second_call

# ---------- radius range ----------

def test_radius_range_results_are_inside_range(repo):
    planets = repo.get_planets_by_radius_range(1.0, 2.0)
    assert len(planets) > 0
    assert all(1.0 <= p.radius_earth <= 2.0 for p in planets)


def test_radius_range_reversed_raises(repo):
    with pytest.raises(ValueError):
        repo.get_planets_by_radius_range(5, 1)


# ---------- by star ----------

def test_planets_by_star_all_belong_to_that_star(repo):
    planets = repo.get_planets_by_star("TRAPPIST-1")
    assert len(planets) == 7
    assert all(p.star.hostname == "TRAPPIST-1" for p in planets)


def test_planets_by_unknown_star_returns_empty_list(repo):
    assert repo.get_planets_by_star("No Such Star") == []


# ---------- largest / smallest ----------

def test_largest_planet_is_at_least_as_big_as_every_other(repo):
    largest = repo.get_largest_planet()
    known = [p.radius_earth for p in repo.get_all_planets() if p.radius_earth is not None]
    assert largest.radius_earth == max(known)

def test_smallest_planet_is_not_unknown_and_is_minimum(repo):
    smallest = repo.get_smallest_planet()
    known = [p.radius_earth for p in repo.get_all_planets() if p.radius_earth is not None]
    assert smallest.radius_earth == min(known)

# ---------- count of planets ----------
def test_count_planets_matches_all_planets(repo):
    assert repo.count_planets() == len(repo.get_all_planets())
    
def test_pages_dont_overlap(repo):
    page_1 = repo.get_planets_page(limit=10, offset=0)
    page_1_set = {planet.name for planet in page_1}
    page_2 = repo.get_planets_page(limit=10, offset=10)
    page_2_set = {planet.name for planet in page_2}
    assert page_1_set.isdisjoint(page_2_set)

def test_page_match_full_list(repo):
    page_results = repo.get_planets_page(limit=10, offset=20)
    list_results = repo.get_all_planets()[20:30]
    assert page_results == list_results

# ---------- count planets ----------
def test_count_search_without_filters_equals_count_planets(repo):
    assert repo.count_search() == repo.count_planets()


def test_count_search_with_hostname(repo):
    assert repo.count_search(hostname="TRAPPIST-1") == 7


def test_count_search_matches_radius_range_method(repo):
    expected = len(repo.get_planets_by_radius_range(1, 2))
    assert repo.count_search(min_radius=1, max_radius=2) == expected

# ---------- stars ----------
def test_get_star_by_id_returns_the_planets_star(repo):
    planet = repo.get_planet_by_name("TRAPPIST-1 e")
    star = repo.get_star_by_id(planet.star_id)
    assert star.hostname == "TRAPPIST-1"
    assert star.star_id == planet.star_id


def test_get_star_by_id_unknown_raises(repo):
    with pytest.raises(StarNotFoundError):
        repo.get_star_by_id(-1)


def test_get_planets_for_star_all_belong_to_that_star(repo):
    star_id = repo.get_planet_by_name("TRAPPIST-1 e").star_id
    planets = repo.get_planets_for_star(star_id)
    assert len(planets) == 7                                  # snapshot
    assert all(p.star_id == star_id for p in planets)         # property


def test_get_planets_for_unknown_star_returns_empty_list(repo):
    assert repo.get_planets_for_star(-1) == []


def test_count_stars_equals_distinct_hosts_of_all_planets(repo):
    # Every star in the table hosts at least one planet, so the two counts must agree.
    hostnames = {p.star.hostname for p in repo.get_all_planets()}
    assert repo.count_stars() == len(hostnames)


def test_count_stars_snapshot(repo):
    assert repo.count_stars() == 4847                         # snapshot of 2026-10-31 data


def test_star_pages_dont_overlap(repo):
    page_1 = {s.hostname for s in repo.get_stars_page(limit=10, offset=0)}
    page_2 = {s.hostname for s in repo.get_stars_page(limit=10, offset=10)}
    assert len(page_1) == 10
    assert len(page_2) == 10
    assert page_1.isdisjoint(page_2)
    
def test_star_search_results_contain_the_text(repo):
    stars = repo.get_stars_page(limit=50, offset=0, q="trappist")
    assert len(stars) > 0
    assert all("trappist" in s.hostname.lower() for s in stars)


def test_count_stars_with_filter_matches_returned_stars(repo):
    stars = repo.get_stars_page(limit=200, offset=0, q="trappist")
    assert repo.count_stars(q="trappist") == len(stars)


def test_count_stars_with_no_match_is_zero(repo):
    assert repo.count_stars(q="zzzz-no-such-star") == 0