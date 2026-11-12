from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_get_planet_returns_planet_with_star():
    response = client.get("/planets/TRAPPIST-1 e")
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "TRAPPIST-1 e"
    assert body["category"] == "Earth-like"
    assert body["star"]["hostname"] == "TRAPPIST-1"


def test_get_unknown_planet_is_404():
    response = client.get("/planets/Fake Planet")
    assert response.status_code == 404
    assert "Fake Planet" in response.json()["detail"]


def test_list_planets_is_paginated():
    response = client.get("/planets", params={"limit": 5, "offset": 0})
    body = response.json()
    assert response.status_code == 200
    assert len(body["items"]) == 5
    assert body["total"] == 6451                      # snapshot
    assert body["limit"] == 5


def test_limit_above_maximum_is_422():
    assert client.get("/planets", params={"limit": 500}).status_code == 422


def test_search_reversed_range_is_422():
    response = client.get("/planets/search", params={"min_radius": 5, "max_radius": 1})
    assert response.status_code == 422


def test_search_by_name_finds_trappist_planets():
    body = client.get("/planets/search", params={"q": "trappist"}).json()
    assert body["total"] == 7                         # snapshot
    assert all("trappist" in p["name"].lower() for p in body["items"])


def test_largest_planet():
    body = client.get("/planets/largest").json()
    assert body["name"] == "V2376 Ori b"              # snapshot


def test_missing_values_are_null_in_json():
    # Find a planet with no radius through the API itself.
    # YOUR TURN: pick one such planet name from Workbench, request it,
    # and assert that body["radius_earth"] is None and body["category"] == "Unknown".
    ...


def test_star_search_filters_by_name():
    body = client.get("/stars", params={"q": "trappist"}).json()
    assert body["total"] == 1


def test_star_detail_includes_its_planets():
    star_id = client.get("/planets/TRAPPIST-1 e").json()["star_id"]
    body = client.get(f"/stars/{star_id}").json()
    assert body["hostname"] == "TRAPPIST-1"
    assert body["planet_count"] == 7
    assert len(body["planets"]) == 7


def test_unknown_star_is_404():
    assert client.get("/stars/-1").status_code == 404


def test_statistics():
    body = client.get("/statistics").json()
    assert body["total_planets"] == 6451              # snapshot
    assert body["radius"]["count"] == 6401            # snapshot
    assert sum(body["category_counts"].values()) == body["total_planets"]
    assert set(body["category_counts"]) == {
        "Earth-like", "Super-Earth", "Neptune-like", "Giant", "Unknown"
    }

def test_compare_returns_planets_in_requested_order():
    response = client.post("/planets/compare",
                           json={"names": ["TRAPPIST-1 f", "TRAPPIST-1 e"]})
    assert response.status_code == 200
    names = [p["name"] for p in response.json()["planets"]]
    assert names == ["TRAPPIST-1 f", "TRAPPIST-1 e"]


def test_compare_with_one_name_is_422():
    response = client.post("/planets/compare", json={"names": ["TRAPPIST-1 e"]})
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "names"]


def test_compare_with_five_names_is_422():
    names = ["a", "b", "c", "d", "e"]
    assert client.post("/planets/compare", json={"names": names}).status_code == 422


def test_compare_duplicates_is_422():
    body = {"names": ["TRAPPIST-1 e", "TRAPPIST-1 e"]}
    response = client.post("/planets/compare", json=body)
    assert response.status_code == 422
    assert "Duplicate" in response.json()["detail"]


def test_compare_unknown_planet_is_404():
    body = {"names": ["TRAPPIST-1 e", "Fake Planet"]}
    response = client.post("/planets/compare", json=body)
    assert response.status_code == 404
    assert "Fake Planet" in response.json()["detail"]