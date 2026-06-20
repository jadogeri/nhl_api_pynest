"""
Unit tests for TeamController.
TeamService is fully mocked — controller methods are invoked directly
(not via HTTP) to isolate routing logic from business logic.
"""
import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException

from src.modules.team.team_controller import TeamController
from src.modules.team.team_service import TeamService
from src.modules.team.team_entity import TeamEntity
from src.modules.team.team_model import Team, TeamUpdate, TeamResponse


def make_team_response(
    id=1,
    name="Boston Bruins",
    city="Boston",
    state="MA",
    conference="Eastern",
    division="Atlantic",
    stadium="TD Garden",
):
    return TeamResponse(
        id=id,
        name=name,
        city=city,
        state=state,
        conference=conference,
        division=division,
        stadium=stadium,
    )


@pytest.fixture
def mock_service():
    return MagicMock(spec=TeamService)


@pytest.fixture
def controller(mock_service):
    return TeamController(team_service=mock_service)


class TestReadTeams:

    def test_read_teams_no_filters(self, controller, mock_service):
        expected = [make_team_response()]
        mock_service.list_teams.return_value = expected

        result = controller.read_teams()

        mock_service.list_teams.assert_called_once_with(conference=None, division=None)
        assert result == expected

    def test_read_teams_with_conference_filter(self, controller, mock_service):
        mock_service.list_teams.return_value = []

        controller.read_teams(conference="Eastern")

        mock_service.list_teams.assert_called_once_with(conference="Eastern", division=None)

    def test_read_teams_with_division_filter(self, controller, mock_service):
        mock_service.list_teams.return_value = []

        controller.read_teams(division="Atlantic")

        mock_service.list_teams.assert_called_once_with(conference=None, division="Atlantic")

    def test_read_teams_with_both_filters(self, controller, mock_service):
        mock_service.list_teams.return_value = []

        controller.read_teams(conference="Eastern", division="Atlantic")

        mock_service.list_teams.assert_called_once_with(conference="Eastern", division="Atlantic")

    def test_read_teams_returns_service_result(self, controller, mock_service):
        teams = [make_team_response(i, name=f"Team {i}", city="City") for i in range(1, 4)]
        mock_service.list_teams.return_value = teams

        result = controller.read_teams()

        assert result == teams
        assert len(result) == 3

    def test_read_teams_empty_list(self, controller, mock_service):
        mock_service.list_teams.return_value = []

        result = controller.read_teams()

        assert result == []


class TestReadTeam:

    def test_read_team_delegates_to_service(self, controller, mock_service):
        expected = make_team_response(id=5)
        mock_service.get_team.return_value = expected

        result = controller.read_team(5)

        mock_service.get_team.assert_called_once_with(5)
        assert result == expected

    def test_read_team_propagates_404(self, controller, mock_service):
        mock_service.get_team.side_effect = HTTPException(status_code=404, detail="Team not found")

        with pytest.raises(HTTPException) as exc_info:
            controller.read_team(999)

        assert exc_info.value.status_code == 404

    def test_read_team_returns_correct_team(self, controller, mock_service):
        expected = make_team_response(id=3, name="Chicago Blackhawks", city="Chicago")
        mock_service.get_team.return_value = expected

        result = controller.read_team(3)

        assert result.name == "Chicago Blackhawks"


class TestAddTeam:

    def test_add_team_delegates_to_service(self, controller, mock_service):
        team_input = Team(
            name="Vegas Golden Knights",
            city="Las Vegas",
            state="NV",
            conference="Western",
            division="Pacific",
        )
        expected = make_team_response(id=31, name="Vegas Golden Knights", city="Las Vegas", state="NV", conference="Western", division="Pacific", stadium=None)
        mock_service.add_team.return_value = expected

        result = controller.add_team(team_input)

        mock_service.add_team.assert_called_once_with(team_input)
        assert result == expected

    def test_add_team_propagates_400_on_duplicate(self, controller, mock_service):
        mock_service.add_team.side_effect = HTTPException(
            status_code=400, detail="Team 'Boston Bruins' already exists."
        )
        team_input = Team(
            name="Boston Bruins",
            city="Boston",
            conference="Eastern",
            division="Atlantic",
        )

        with pytest.raises(HTTPException) as exc_info:
            controller.add_team(team_input)

        assert exc_info.value.status_code == 400

    def test_add_team_returns_created_team(self, controller, mock_service):
        team_input = Team(
            name="Seattle Kraken",
            city="Seattle",
            state="WA",
            conference="Western",
            division="Pacific",
        )
        expected = make_team_response(id=32, name="Seattle Kraken", city="Seattle", state="WA", conference="Western", division="Pacific", stadium=None)
        mock_service.add_team.return_value = expected

        result = controller.add_team(team_input)

        assert result.id == 32
        assert result.name == "Seattle Kraken"


class TestUpdateExistingTeam:

    def test_update_team_delegates_to_service(self, controller, mock_service):
        update = TeamUpdate(stadium="New Arena")
        expected = make_team_response(id=1, stadium="New Arena")
        mock_service.modify_team.return_value = expected

        result = controller.update_existing_team(1, update)

        mock_service.modify_team.assert_called_once_with(1, update)
        assert result == expected

    def test_update_team_propagates_404(self, controller, mock_service):
        mock_service.modify_team.side_effect = HTTPException(
            status_code=404, detail="Team not found"
        )

        with pytest.raises(HTTPException) as exc_info:
            controller.update_existing_team(999, TeamUpdate(city="Nowhere"))

        assert exc_info.value.status_code == 404

    def test_update_team_partial_update(self, controller, mock_service):
        update = TeamUpdate(city="New City")
        expected = make_team_response(id=2, city="New City")
        mock_service.modify_team.return_value = expected

        result = controller.update_existing_team(2, update)

        mock_service.modify_team.assert_called_once_with(2, update)


class TestDeleteExistingTeam:

    def test_delete_team_delegates_to_service(self, controller, mock_service):
        mock_service.remove_team.return_value = {"message": "Team deleted successfully"}

        result = controller.delete_existing_team(1)

        mock_service.remove_team.assert_called_once_with(1)
        assert result == {"message": "Team deleted successfully"}

    def test_delete_team_propagates_404(self, controller, mock_service):
        mock_service.remove_team.side_effect = HTTPException(
            status_code=404, detail="Team not found"
        )

        with pytest.raises(HTTPException) as exc_info:
            controller.delete_existing_team(999)

        assert exc_info.value.status_code == 404

    def test_delete_team_returns_message(self, controller, mock_service):
        mock_service.remove_team.return_value = {"message": "Team deleted successfully"}

        result = controller.delete_existing_team(5)

        assert "deleted" in result["message"]


class TestPopulateDatabase:

    def test_populate_database_delegates_to_service(self, controller, mock_service):
        mock_service.populate_from_file.return_value = {
            "message": "Populated successfully. Added 30 unique teams."
        }

        result = controller.populate_database()

        mock_service.populate_from_file.assert_called_once()
        assert "30" in result["message"]

    def test_populate_database_propagates_500_on_missing_file(self, controller, mock_service):
        mock_service.populate_from_file.side_effect = HTTPException(
            status_code=500, detail="Source file 'nhl_teams.json' not found."
        )

        with pytest.raises(HTTPException) as exc_info:
            controller.populate_database()

        assert exc_info.value.status_code == 500


class TestTruncateDatabase:

    def test_truncate_database_delegates_to_service(self, controller, mock_service):
        mock_service.clear_all_teams.return_value = {
            "message": "All team database records dropped successfully."
        }

        result = controller.truncate_database()

        mock_service.clear_all_teams.assert_called_once()
        assert "dropped" in result["message"]
