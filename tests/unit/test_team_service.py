"""
Unit tests for TeamService.
TeamRepository is fully mocked — no database calls are made.
All HTTPException raises are tested against status_code and detail.
"""
import pytest
import json
import os
from unittest.mock import MagicMock, patch, mock_open
from fastapi import HTTPException

from src.modules.team.team_service import TeamService
from src.modules.team.team_repository import TeamRepository
from src.modules.team.team_entity import TeamEntity
from src.modules.team.team_model import Team, TeamUpdate, TeamResponse


def make_team_entity(
    id=1,
    name="Boston Bruins",
    city="Boston",
    state="MA",
    conference="Eastern",
    division="Atlantic",
    stadium="TD Garden",
):
    entity = TeamEntity(
        name=name,
        city=city,
        state=state,
        conference=conference,
        division=division,
        stadium=stadium,
    )
    entity.id = id
    return entity


@pytest.fixture
def mock_repo():
    return MagicMock(spec=TeamRepository)


@pytest.fixture
def service(mock_repo):
    return TeamService(repository=mock_repo)


class TestListTeams:

    def test_list_teams_returns_team_response_list(self, service, mock_repo):
        entity = make_team_entity()
        mock_repo.get_all_teams.return_value = [entity]

        result = service.list_teams()

        mock_repo.get_all_teams.assert_called_once_with(None, None)
        assert len(result) == 1
        assert isinstance(result[0], TeamResponse)
        assert result[0].id == 1
        assert result[0].name == "Boston Bruins"

    def test_list_teams_with_conference_filter(self, service, mock_repo):
        mock_repo.get_all_teams.return_value = [make_team_entity()]

        service.list_teams(conference="Eastern")

        mock_repo.get_all_teams.assert_called_once_with("Eastern", None)

    def test_list_teams_with_division_filter(self, service, mock_repo):
        mock_repo.get_all_teams.return_value = [make_team_entity()]

        service.list_teams(division="Atlantic")

        mock_repo.get_all_teams.assert_called_once_with(None, "Atlantic")

    def test_list_teams_with_both_filters(self, service, mock_repo):
        mock_repo.get_all_teams.return_value = []

        result = service.list_teams(conference="Eastern", division="Atlantic")

        mock_repo.get_all_teams.assert_called_once_with("Eastern", "Atlantic")
        assert result == []

    def test_list_teams_empty_repository(self, service, mock_repo):
        mock_repo.get_all_teams.return_value = []

        result = service.list_teams()

        assert result == []

    def test_list_teams_returns_multiple(self, service, mock_repo):
        entities = [make_team_entity(i, name=f"Team {i}", city="City") for i in range(1, 4)]
        mock_repo.get_all_teams.return_value = entities

        result = service.list_teams()

        assert len(result) == 3


class TestGetTeam:

    def test_get_team_found(self, service, mock_repo):
        entity = make_team_entity(id=5)
        mock_repo.get_team_by_id.return_value = entity

        result = service.get_team(5)

        mock_repo.get_team_by_id.assert_called_once_with(5)
        assert isinstance(result, TeamResponse)
        assert result.id == 5

    def test_get_team_not_found_raises_404(self, service, mock_repo):
        mock_repo.get_team_by_id.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            service.get_team(999)

        assert exc_info.value.status_code == 404
        assert "Team not found" in exc_info.value.detail

    def test_get_team_calls_repository_with_correct_id(self, service, mock_repo):
        mock_repo.get_team_by_id.return_value = make_team_entity(id=7)

        service.get_team(7)

        mock_repo.get_team_by_id.assert_called_once_with(7)


class TestAddTeam:

    def test_add_team_success(self, service, mock_repo):
        mock_repo.get_team_by_name.return_value = None
        new_entity = make_team_entity(id=31, name="Vegas Golden Knights", city="Las Vegas")
        mock_repo.create_team.return_value = new_entity

        team_data = Team(
            name="Vegas Golden Knights",
            city="Las Vegas",
            state="NV",
            conference="Western",
            division="Pacific",
        )

        result = service.add_team(team_data)

        mock_repo.get_team_by_name.assert_called_once_with("Vegas Golden Knights")
        mock_repo.create_team.assert_called_once_with(team_data)
        assert isinstance(result, TeamResponse)
        assert result.id == 31

    def test_add_team_duplicate_name_raises_400(self, service, mock_repo):
        existing = make_team_entity(name="Boston Bruins")
        mock_repo.get_team_by_name.return_value = existing

        team_data = Team(
            name="Boston Bruins",
            city="Boston",
            conference="Eastern",
            division="Atlantic",
        )

        with pytest.raises(HTTPException) as exc_info:
            service.add_team(team_data)

        assert exc_info.value.status_code == 400
        assert "Boston Bruins" in exc_info.value.detail

    def test_add_team_duplicate_does_not_call_create(self, service, mock_repo):
        mock_repo.get_team_by_name.return_value = make_team_entity()

        with pytest.raises(HTTPException):
            service.add_team(
                Team(name="Boston Bruins", city="Boston", conference="Eastern", division="Atlantic")
            )

        mock_repo.create_team.assert_not_called()


class TestModifyTeam:

    def test_modify_team_success(self, service, mock_repo):
        existing = make_team_entity(id=1, stadium="Old Arena")
        updated = make_team_entity(id=1, stadium="New Arena")
        mock_repo.get_team_by_id.return_value = existing
        mock_repo.update_team.return_value = updated

        result = service.modify_team(1, TeamUpdate(stadium="New Arena"))

        mock_repo.get_team_by_id.assert_called_once_with(1)
        mock_repo.update_team.assert_called_once_with(existing, TeamUpdate(stadium="New Arena"))
        assert isinstance(result, TeamResponse)
        assert result.stadium == "New Arena"

    def test_modify_team_not_found_raises_404(self, service, mock_repo):
        mock_repo.get_team_by_id.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            service.modify_team(999, TeamUpdate(city="New City"))

        assert exc_info.value.status_code == 404
        assert "Team not found" in exc_info.value.detail

    def test_modify_team_not_found_does_not_call_update(self, service, mock_repo):
        mock_repo.get_team_by_id.return_value = None

        with pytest.raises(HTTPException):
            service.modify_team(999, TeamUpdate(city="New City"))

        mock_repo.update_team.assert_not_called()


class TestRemoveTeam:

    def test_remove_team_success(self, service, mock_repo):
        entity = make_team_entity(id=1)
        mock_repo.get_team_by_id.return_value = entity

        result = service.remove_team(1)

        mock_repo.get_team_by_id.assert_called_once_with(1)
        mock_repo.delete_team.assert_called_once_with(entity)
        assert result == {"message": "Team deleted successfully"}

    def test_remove_team_not_found_raises_404(self, service, mock_repo):
        mock_repo.get_team_by_id.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            service.remove_team(999)

        assert exc_info.value.status_code == 404
        assert "Team not found" in exc_info.value.detail

    def test_remove_team_not_found_does_not_call_delete(self, service, mock_repo):
        mock_repo.get_team_by_id.return_value = None

        with pytest.raises(HTTPException):
            service.remove_team(999)

        mock_repo.delete_team.assert_not_called()


class TestPopulateFromFile:

    def test_populate_from_file_success(self, service, mock_repo):
        teams_json = json.dumps(
            {
                "nhl_teams": [
                    {"name": "Boston Bruins", "city": "Boston", "state": "MA", "conference": "Eastern", "division": "Atlantic", "stadium": "TD Garden"},
                    {"name": "Buffalo Sabres", "city": "Buffalo", "state": "NY", "conference": "Eastern", "division": "Atlantic", "stadium": "KeyBank Center"},
                ]
            }
        )
        mock_repo.get_team_by_name.return_value = None
        mock_repo.create_team.return_value = make_team_entity()

        with patch("os.path.exists", return_value=True), \
             patch("builtins.open", mock_open(read_data=teams_json)):
            result = service.populate_from_file("nhl_teams.json")

        assert result["message"].startswith("Populated successfully")
        assert "2" in result["message"]
        assert mock_repo.create_team.call_count == 2

    def test_populate_from_file_skips_duplicates(self, service, mock_repo):
        teams_json = json.dumps(
            {
                "nhl_teams": [
                    {"name": "Boston Bruins", "city": "Boston", "state": "MA", "conference": "Eastern", "division": "Atlantic"},
                ]
            }
        )
        mock_repo.get_team_by_name.return_value = make_team_entity()

        with patch("os.path.exists", return_value=True), \
             patch("builtins.open", mock_open(read_data=teams_json)):
            result = service.populate_from_file("nhl_teams.json")

        assert "0" in result["message"]
        mock_repo.create_team.assert_not_called()

    def test_populate_from_file_not_found_raises_500(self, service, mock_repo):
        with patch("os.path.exists", return_value=False):
            with pytest.raises(HTTPException) as exc_info:
                service.populate_from_file("missing.json")

        assert exc_info.value.status_code == 500
        assert "missing.json" in exc_info.value.detail

    def test_populate_from_file_empty_teams_list(self, service, mock_repo):
        teams_json = json.dumps({"nhl_teams": []})

        with patch("os.path.exists", return_value=True), \
             patch("builtins.open", mock_open(read_data=teams_json)):
            result = service.populate_from_file("nhl_teams.json")

        assert "0" in result["message"]
        mock_repo.create_team.assert_not_called()


class TestClearAllTeams:

    def test_clear_all_teams_calls_truncate(self, service, mock_repo):
        result = service.clear_all_teams()

        mock_repo.truncate_teams.assert_called_once()
        assert result == {"message": "All team database records dropped successfully."}

    def test_clear_all_teams_returns_correct_message(self, service, mock_repo):
        result = service.clear_all_teams()

        assert "dropped" in result["message"]
