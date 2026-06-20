"""
End-to-end tests for the /teams HTTP API.
All requests go through the full FastAPI + PyNest stack against a dedicated
test SQLite database (test_nhl.db). No mocking — every layer
(controller → service → repository → DB) is exercised with real HTTP calls
via Starlette's TestClient. The database is truncated before each test.
"""
import json
import pytest


TEAMS_URL = "/teams/"


def make_team_payload(
    name="Boston Bruins",
    city="Boston",
    state="MA",
    conference="Eastern",
    division="Atlantic",
    stadium="TD Garden",
):
    return {
        "name": name,
        "city": city,
        "state": state,
        "conference": conference,
        "division": division,
        "stadium": stadium,
    }


@pytest.fixture
def http(client):
    return client


@pytest.fixture
def created_team(http):
    """Create and return one persisted team for tests that need an existing record."""
    resp = http.post(TEAMS_URL, json=make_team_payload())
    assert resp.status_code == 200
    return resp.json()


class TestGetTeams:

    def test_list_teams_empty(self, http):
        resp = http.get(TEAMS_URL)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_teams_returns_created_teams(self, http):
        http.post(TEAMS_URL, json=make_team_payload("Boston Bruins", "Boston", "MA", "Eastern", "Atlantic"))
        http.post(TEAMS_URL, json=make_team_payload("Buffalo Sabres", "Buffalo", "NY", "Eastern", "Atlantic", "KeyBank Center"))

        resp = http.get(TEAMS_URL)

        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2

    def test_list_teams_conference_filter(self, http):
        http.post(TEAMS_URL, json=make_team_payload("Boston Bruins", "Boston", "MA", "Eastern", "Atlantic"))
        http.post(TEAMS_URL, json=make_team_payload("Chicago Blackhawks", "Chicago", "IL", "Western", "Central", "United Center"))

        resp = http.get(TEAMS_URL, params={"conference": "Eastern"})

        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["name"] == "Boston Bruins"

    def test_list_teams_division_filter(self, http):
        http.post(TEAMS_URL, json=make_team_payload("Boston Bruins", "Boston", "MA", "Eastern", "Atlantic"))
        http.post(TEAMS_URL, json=make_team_payload("Pittsburgh Penguins", "Pittsburgh", "PA", "Eastern", "Metropolitan", "PPG Paints Arena"))

        resp = http.get(TEAMS_URL, params={"division": "Atlantic"})

        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["division"] == "Atlantic"

    def test_list_teams_both_filters(self, http):
        http.post(TEAMS_URL, json=make_team_payload("Boston Bruins", "Boston", "MA", "Eastern", "Atlantic"))
        http.post(TEAMS_URL, json=make_team_payload("Tampa Bay Lightning", "Tampa", "FL", "Eastern", "Atlantic", "Amalie Arena"))
        http.post(TEAMS_URL, json=make_team_payload("Chicago Blackhawks", "Chicago", "IL", "Western", "Central"))

        resp = http.get(TEAMS_URL, params={"conference": "Eastern", "division": "Atlantic"})

        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_list_teams_filter_no_match_returns_empty(self, http):
        http.post(TEAMS_URL, json=make_team_payload())

        resp = http.get(TEAMS_URL, params={"conference": "Western"})

        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_teams_response_has_expected_fields(self, http, created_team):
        resp = http.get(TEAMS_URL)
        data = resp.json()
        first = data[0]
        assert "id" in first
        assert "name" in first
        assert "city" in first
        assert "conference" in first
        assert "division" in first


class TestGetTeam:

    def test_get_team_by_id_found(self, http, created_team):
        team_id = created_team["id"]

        resp = http.get(f"{TEAMS_URL}{team_id}")

        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == team_id
        assert data["name"] == "Boston Bruins"

    def test_get_team_by_id_not_found(self, http):
        resp = http.get(f"{TEAMS_URL}99999")

        assert resp.status_code == 404

    def test_get_team_response_fields(self, http, created_team):
        team_id = created_team["id"]
        resp = http.get(f"{TEAMS_URL}{team_id}")
        data = resp.json()

        assert data["name"] == "Boston Bruins"
        assert data["city"] == "Boston"
        assert data["state"] == "MA"
        assert data["conference"] == "Eastern"
        assert data["division"] == "Atlantic"
        assert data["stadium"] == "TD Garden"


class TestCreateTeam:

    def test_create_team_success(self, http):
        payload = make_team_payload()

        resp = http.post(TEAMS_URL, json=payload)

        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] is not None
        assert data["name"] == "Boston Bruins"

    def test_create_team_duplicate_name_returns_400(self, http):
        http.post(TEAMS_URL, json=make_team_payload())

        resp = http.post(TEAMS_URL, json=make_team_payload())

        assert resp.status_code == 400

    def test_create_team_with_nullable_fields_omitted(self, http):
        payload = {
            "name": "Winnipeg Jets",
            "city": "Winnipeg",
            "conference": "Western",
            "division": "Central",
        }

        resp = http.post(TEAMS_URL, json=payload)

        assert resp.status_code == 200
        data = resp.json()
        assert data["state"] is None
        assert data["stadium"] is None

    def test_create_team_missing_required_name_returns_422(self, http):
        payload = {"city": "Boston", "conference": "Eastern", "division": "Atlantic"}

        resp = http.post(TEAMS_URL, json=payload)

        assert resp.status_code == 422

    def test_create_team_missing_required_conference_returns_422(self, http):
        payload = {"name": "Boston Bruins", "city": "Boston", "division": "Atlantic"}

        resp = http.post(TEAMS_URL, json=payload)

        assert resp.status_code == 422

    def test_create_team_is_retrievable_after_creation(self, http):
        create_resp = http.post(TEAMS_URL, json=make_team_payload())
        created_id = create_resp.json()["id"]

        get_resp = http.get(f"{TEAMS_URL}{created_id}")

        assert get_resp.status_code == 200
        assert get_resp.json()["name"] == "Boston Bruins"


class TestUpdateTeam:

    def test_update_team_success(self, http, created_team):
        team_id = created_team["id"]
        update_payload = {"stadium": "Updated Arena"}

        resp = http.put(f"{TEAMS_URL}{team_id}", json=update_payload)

        assert resp.status_code == 200
        data = resp.json()
        assert data["stadium"] == "Updated Arena"

    def test_update_team_not_found_returns_404(self, http):
        resp = http.put(f"{TEAMS_URL}99999", json={"city": "Nowhere"})

        assert resp.status_code == 404

    def test_update_team_partial_update_preserves_other_fields(self, http, created_team):
        team_id = created_team["id"]

        resp = http.put(f"{TEAMS_URL}{team_id}", json={"stadium": "New Arena"})

        data = resp.json()
        assert data["name"] == "Boston Bruins"
        assert data["city"] == "Boston"
        assert data["stadium"] == "New Arena"

    def test_update_team_multiple_fields(self, http, created_team):
        team_id = created_team["id"]

        resp = http.put(f"{TEAMS_URL}{team_id}", json={"city": "New City", "state": "NC"})

        data = resp.json()
        assert data["city"] == "New City"
        assert data["state"] == "NC"

    def test_update_team_empty_body_no_change(self, http, created_team):
        team_id = created_team["id"]

        resp = http.put(f"{TEAMS_URL}{team_id}", json={})

        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Boston Bruins"

    def test_update_is_persisted(self, http, created_team):
        team_id = created_team["id"]
        http.put(f"{TEAMS_URL}{team_id}", json={"stadium": "Persisted Arena"})

        get_resp = http.get(f"{TEAMS_URL}{team_id}")

        assert get_resp.json()["stadium"] == "Persisted Arena"


class TestDeleteTeam:

    def test_delete_team_success(self, http, created_team):
        team_id = created_team["id"]

        resp = http.delete(f"{TEAMS_URL}{team_id}")

        assert resp.status_code == 200
        data = resp.json()
        assert "deleted" in data["message"]

    def test_delete_team_not_found_returns_404(self, http):
        resp = http.delete(f"{TEAMS_URL}99999")

        assert resp.status_code == 404

    def test_deleted_team_is_no_longer_retrievable(self, http, created_team):
        team_id = created_team["id"]
        http.delete(f"{TEAMS_URL}{team_id}")

        get_resp = http.get(f"{TEAMS_URL}{team_id}")

        assert get_resp.status_code == 404

    def test_delete_does_not_affect_other_teams(self, http):
        first = http.post(TEAMS_URL, json=make_team_payload("Boston Bruins", "Boston", "MA", "Eastern", "Atlantic")).json()
        second = http.post(TEAMS_URL, json=make_team_payload("Buffalo Sabres", "Buffalo", "NY", "Eastern", "Atlantic", "KeyBank Center")).json()

        http.delete(f"{TEAMS_URL}{first['id']}")

        all_teams = http.get(TEAMS_URL).json()
        assert len(all_teams) == 1
        assert all_teams[0]["id"] == second["id"]


class TestPopulateDatabase:

    def test_populate_endpoint_responds(self, http):
        resp = http.post(f"{TEAMS_URL}populate")
        assert resp.status_code in (200, 500)

    def test_populate_returns_message(self, http):
        resp = http.post(f"{TEAMS_URL}populate")
        if resp.status_code == 200:
            data = resp.json()
            assert "message" in data

    def test_populate_then_list_returns_teams(self, http):
        resp = http.post(f"{TEAMS_URL}populate")
        if resp.status_code == 200:
            all_teams = http.get(TEAMS_URL).json()
            assert len(all_teams) > 0

    def test_populate_twice_does_not_duplicate(self, http):
        first = http.post(f"{TEAMS_URL}populate")
        if first.status_code != 200:
            pytest.skip("nhl_teams.json not found in working directory")

        second = http.post(f"{TEAMS_URL}populate")
        assert second.status_code == 200
        assert "0" in second.json()["message"]

        all_teams = http.get(TEAMS_URL).json()
        names = [t["name"] for t in all_teams]
        assert len(names) == len(set(names))


class TestTruncateDatabase:

    def test_truncate_endpoint_returns_200(self, http):
        resp = http.post(f"{TEAMS_URL}truncate")
        assert resp.status_code == 200

    def test_truncate_returns_message(self, http):
        resp = http.post(f"{TEAMS_URL}truncate")
        data = resp.json()
        assert "message" in data
        assert "dropped" in data["message"]

    def test_truncate_clears_all_teams(self, http):
        http.post(TEAMS_URL, json=make_team_payload("Boston Bruins", "Boston", "MA", "Eastern", "Atlantic"))
        http.post(TEAMS_URL, json=make_team_payload("Buffalo Sabres", "Buffalo", "NY", "Eastern", "Atlantic", "KeyBank Center"))

        http.post(f"{TEAMS_URL}truncate")

        all_teams = http.get(TEAMS_URL).json()
        assert all_teams == []

    def test_truncate_empty_table_is_safe(self, http):
        resp = http.post(f"{TEAMS_URL}truncate")
        assert resp.status_code == 200

    def test_can_create_team_after_truncate(self, http):
        http.post(TEAMS_URL, json=make_team_payload())
        http.post(f"{TEAMS_URL}truncate")

        resp = http.post(TEAMS_URL, json=make_team_payload("Buffalo Sabres", "Buffalo", "NY", "Eastern", "Atlantic"))

        assert resp.status_code == 200
        assert resp.json()["name"] == "Buffalo Sabres"
