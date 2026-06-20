"""
Integration tests for TeamService with a real TeamRepository.
Uses an in-memory SQLite database. Service and repository are both real instances —
only the database is substituted.

Tests cover full CRUD flows, duplicate detection, populate, and clear operations.
"""
import json
import os
import pytest
from unittest.mock import patch, mock_open
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException

from src.config.database import Base
from src.modules.team.team_repository import TeamRepository
from src.modules.team.team_service import TeamService
from src.modules.team.team_entity import TeamEntity
from src.modules.team.team_model import Team, TeamUpdate, TeamResponse


TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="module")
def engine():
    eng = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=eng)
    yield eng
    Base.metadata.drop_all(bind=eng)


@pytest.fixture(scope="function")
def session_factory(engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def service(session_factory, engine):
    repo = TeamRepository()
    repo.session_factory = session_factory
    svc = TeamService(repository=repo)
    yield svc
    with session_factory() as session:
        session.query(TeamEntity).delete()
        session.commit()


def make_team(
    name="Boston Bruins",
    city="Boston",
    state="MA",
    conference="Eastern",
    division="Atlantic",
    stadium="TD Garden",
):
    return Team(
        name=name, city=city, state=state,
        conference=conference, division=division, stadium=stadium,
    )


class TestListTeamsIntegration:

    def test_list_teams_empty(self, service):
        result = service.list_teams()
        assert result == []

    def test_list_teams_returns_team_responses(self, service):
        service.add_team(make_team())
        result = service.list_teams()
        assert len(result) == 1
        assert isinstance(result[0], TeamResponse)

    def test_list_teams_conference_filter(self, service):
        service.add_team(make_team("Boston Bruins", "Boston", "MA", "Eastern", "Atlantic"))
        service.add_team(make_team("Chicago Blackhawks", "Chicago", "IL", "Western", "Central"))

        result = service.list_teams(conference="Eastern")

        assert len(result) == 1
        assert result[0].name == "Boston Bruins"

    def test_list_teams_division_filter(self, service):
        service.add_team(make_team("Boston Bruins", "Boston", "MA", "Eastern", "Atlantic"))
        service.add_team(make_team("Pittsburgh Penguins", "Pittsburgh", "PA", "Eastern", "Metropolitan", "PPG Paints Arena"))

        result = service.list_teams(division="Atlantic")

        assert len(result) == 1

    def test_list_teams_returns_all(self, service):
        for i in range(5):
            service.add_team(
                make_team(f"Team {i}", f"City {i}", None, "Eastern", "Atlantic", None)
            )

        result = service.list_teams()

        assert len(result) == 5


class TestGetTeamIntegration:

    def test_get_team_found(self, service):
        created = service.add_team(make_team())

        result = service.get_team(created.id)

        assert result.id == created.id
        assert result.name == "Boston Bruins"

    def test_get_team_not_found_raises_404(self, service):
        with pytest.raises(HTTPException) as exc_info:
            service.get_team(99999)

        assert exc_info.value.status_code == 404

    def test_get_team_returns_correct_team_response(self, service):
        created = service.add_team(make_team("Detroit Red Wings", "Detroit", "MI", "Eastern", "Atlantic", "Joe Louis Arena"))

        result = service.get_team(created.id)

        assert isinstance(result, TeamResponse)
        assert result.name == "Detroit Red Wings"
        assert result.stadium == "Joe Louis Arena"


class TestAddTeamIntegration:

    def test_add_team_persists_and_returns_response(self, service):
        result = service.add_team(make_team())

        assert isinstance(result, TeamResponse)
        assert result.id is not None
        assert result.name == "Boston Bruins"

    def test_add_team_duplicate_raises_400(self, service):
        service.add_team(make_team())

        with pytest.raises(HTTPException) as exc_info:
            service.add_team(make_team())

        assert exc_info.value.status_code == 400
        assert "Boston Bruins" in exc_info.value.detail

    def test_add_team_with_nullable_fields(self, service):
        team = Team(name="Winnipeg Jets", city="Winnipeg", conference="Western", division="Central")

        result = service.add_team(team)

        assert result.state is None
        assert result.stadium is None

    def test_add_team_is_retrievable(self, service):
        created = service.add_team(make_team("Tampa Bay Lightning", "Tampa", "FL", "Eastern", "Atlantic", "Amalie Arena"))

        fetched = service.get_team(created.id)

        assert fetched.name == "Tampa Bay Lightning"


class TestModifyTeamIntegration:

    def test_modify_team_updates_field(self, service):
        created = service.add_team(make_team(stadium="Old Arena"))

        result = service.modify_team(created.id, TeamUpdate(stadium="New Arena"))

        assert result.stadium == "New Arena"
        assert result.id == created.id

    def test_modify_team_partial_update_preserves_other_fields(self, service):
        created = service.add_team(make_team("Boston Bruins", "Boston", "MA", "Eastern", "Atlantic", "TD Garden"))

        service.modify_team(created.id, TeamUpdate(stadium="New Arena"))

        fetched = service.get_team(created.id)
        assert fetched.name == "Boston Bruins"
        assert fetched.city == "Boston"
        assert fetched.stadium == "New Arena"

    def test_modify_team_not_found_raises_404(self, service):
        with pytest.raises(HTTPException) as exc_info:
            service.modify_team(99999, TeamUpdate(city="Nowhere"))

        assert exc_info.value.status_code == 404

    def test_modify_team_persisted_after_fetch(self, service):
        created = service.add_team(make_team())
        service.modify_team(created.id, TeamUpdate(city="Updated City"))

        fetched = service.get_team(created.id)

        assert fetched.city == "Updated City"


class TestRemoveTeamIntegration:

    def test_remove_team_deletes_record(self, service):
        created = service.add_team(make_team())

        result = service.remove_team(created.id)

        assert result == {"message": "Team deleted successfully"}
        with pytest.raises(HTTPException):
            service.get_team(created.id)

    def test_remove_team_not_found_raises_404(self, service):
        with pytest.raises(HTTPException) as exc_info:
            service.remove_team(99999)

        assert exc_info.value.status_code == 404

    def test_remove_team_does_not_affect_others(self, service):
        first = service.add_team(make_team("Boston Bruins", "Boston", "MA", "Eastern", "Atlantic"))
        second = service.add_team(make_team("Buffalo Sabres", "Buffalo", "NY", "Eastern", "Atlantic"))

        service.remove_team(first.id)

        remaining = service.list_teams()
        assert len(remaining) == 1
        assert remaining[0].id == second.id


class TestPopulateFromFileIntegration:

    def test_populate_adds_teams(self, service):
        teams_json = json.dumps({
            "nhl_teams": [
                {"name": "Boston Bruins", "city": "Boston", "state": "MA", "conference": "Eastern", "division": "Atlantic", "stadium": "TD Garden"},
                {"name": "Buffalo Sabres", "city": "Buffalo", "state": "NY", "conference": "Eastern", "division": "Atlantic", "stadium": "KeyBank Center"},
            ]
        })

        with patch("os.path.exists", return_value=True), \
             patch("builtins.open", mock_open(read_data=teams_json)):
            result = service.populate_from_file("nhl_teams.json")

        assert "2" in result["message"]
        all_teams = service.list_teams()
        assert len(all_teams) == 2

    def test_populate_skips_existing_teams(self, service):
        service.add_team(make_team("Boston Bruins", "Boston", "MA", "Eastern", "Atlantic"))

        teams_json = json.dumps({
            "nhl_teams": [
                {"name": "Boston Bruins", "city": "Boston", "state": "MA", "conference": "Eastern", "division": "Atlantic"},
                {"name": "Buffalo Sabres", "city": "Buffalo", "state": "NY", "conference": "Eastern", "division": "Atlantic"},
            ]
        })

        with patch("os.path.exists", return_value=True), \
             patch("builtins.open", mock_open(read_data=teams_json)):
            result = service.populate_from_file("nhl_teams.json")

        assert "1" in result["message"]
        all_teams = service.list_teams()
        assert len(all_teams) == 2

    def test_populate_file_not_found_raises_500(self, service):
        with patch("os.path.exists", return_value=False):
            with pytest.raises(HTTPException) as exc_info:
                service.populate_from_file("missing.json")

        assert exc_info.value.status_code == 500


class TestClearAllTeamsIntegration:

    def test_clear_all_teams_empties_table(self, service):
        service.add_team(make_team("Boston Bruins", "Boston", "MA", "Eastern", "Atlantic"))
        service.add_team(make_team("Buffalo Sabres", "Buffalo", "NY", "Eastern", "Atlantic"))

        result = service.clear_all_teams()

        assert result == {"message": "All team database records dropped successfully."}
        assert service.list_teams() == []

    def test_clear_empty_table_is_safe(self, service):
        result = service.clear_all_teams()

        assert result == {"message": "All team database records dropped successfully."}

    def test_can_add_after_clear(self, service):
        service.add_team(make_team())
        service.clear_all_teams()

        new_team = service.add_team(make_team("Buffalo Sabres", "Buffalo", "NY", "Eastern", "Atlantic"))

        assert new_team.id is not None
        assert service.list_teams() == [new_team]
