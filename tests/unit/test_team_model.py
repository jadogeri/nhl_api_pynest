"""
Unit tests for Pydantic models in team_model.py.
No database or external dependencies — pure model validation.
"""
import pytest
from pydantic import ValidationError

from src.modules.team.team_model import Team, TeamCreate, TeamUpdate, TeamResponse
from src.modules.team.team_entity import TeamEntity


class TestTeamModel:

    def test_valid_team_all_fields(self):
        team = Team(
            name="Boston Bruins",
            city="Boston",
            state="MA",
            conference="Eastern",
            division="Atlantic",
            stadium="TD Garden",
        )
        assert team.name == "Boston Bruins"
        assert team.city == "Boston"
        assert team.state == "MA"
        assert team.conference == "Eastern"
        assert team.division == "Atlantic"
        assert team.stadium == "TD Garden"

    def test_valid_team_required_fields_only(self):
        team = Team(
            name="Washington Capitals",
            city="Washington",
            conference="Eastern",
            division="Metropolitan",
        )
        assert team.name == "Washington Capitals"
        assert team.state is None
        assert team.stadium is None

    def test_team_state_defaults_to_none(self):
        team = Team(
            name="Montreal Canadiens",
            city="Montreal",
            conference="Eastern",
            division="Atlantic",
        )
        assert team.state is None

    def test_team_stadium_defaults_to_none(self):
        team = Team(
            name="Ottawa Senators",
            city="Ottawa",
            conference="Eastern",
            division="Atlantic",
        )
        assert team.stadium is None

    def test_team_missing_name_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            Team(city="Boston", conference="Eastern", division="Atlantic")
        assert "name" in str(exc_info.value)

    def test_team_missing_city_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            Team(name="Boston Bruins", conference="Eastern", division="Atlantic")
        assert "city" in str(exc_info.value)

    def test_team_missing_conference_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            Team(name="Boston Bruins", city="Boston", division="Atlantic")
        assert "conference" in str(exc_info.value)

    def test_team_missing_division_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            Team(name="Boston Bruins", city="Boston", conference="Eastern")
        assert "division" in str(exc_info.value)

    def test_team_explicit_none_state(self):
        team = Team(
            name="Boston Bruins",
            city="Boston",
            state=None,
            conference="Eastern",
            division="Atlantic",
        )
        assert team.state is None

    def test_team_explicit_none_stadium(self):
        team = Team(
            name="Boston Bruins",
            city="Boston",
            conference="Eastern",
            division="Atlantic",
            stadium=None,
        )
        assert team.stadium is None


class TestTeamCreateModel:

    def test_team_create_is_subclass_of_team(self):
        assert issubclass(TeamCreate, Team)

    def test_team_create_valid(self):
        tc = TeamCreate(
            name="Chicago Blackhawks",
            city="Chicago",
            state="IL",
            conference="Western",
            division="Central",
            stadium="United Center",
        )
        assert tc.name == "Chicago Blackhawks"
        assert tc.stadium == "United Center"

    def test_team_create_optional_fields_default_none(self):
        tc = TeamCreate(
            name="Winnipeg Jets",
            city="Winnipeg",
            conference="Western",
            division="Central",
        )
        assert tc.state is None
        assert tc.stadium is None


class TestTeamUpdateModel:

    def test_team_update_all_fields_optional(self):
        update = TeamUpdate()
        assert update.name is None
        assert update.city is None
        assert update.state is None
        assert update.conference is None
        assert update.division is None
        assert update.stadium is None

    def test_team_update_partial_name(self):
        update = TeamUpdate(name="Vegas Golden Knights")
        assert update.name == "Vegas Golden Knights"
        assert update.city is None

    def test_team_update_partial_stadium(self):
        update = TeamUpdate(stadium="New Arena")
        assert update.stadium == "New Arena"
        assert update.name is None

    def test_team_update_all_fields(self):
        update = TeamUpdate(
            name="New Name",
            city="New City",
            state="NC",
            conference="Eastern",
            division="Metropolitan",
            stadium="New Stadium",
        )
        assert update.name == "New Name"
        assert update.city == "New City"
        assert update.state == "NC"
        assert update.conference == "Eastern"
        assert update.division == "Metropolitan"
        assert update.stadium == "New Stadium"

    def test_team_update_model_dump_exclude_unset(self):
        update = TeamUpdate(stadium="Bell Centre")
        dumped = update.model_dump(exclude_unset=True)
        assert dumped == {"stadium": "Bell Centre"}
        assert "name" not in dumped

    def test_team_update_empty_model_dump_exclude_unset(self):
        update = TeamUpdate()
        dumped = update.model_dump(exclude_unset=True)
        assert dumped == {}


class TestTeamResponseModel:

    def test_team_response_requires_id(self):
        with pytest.raises(ValidationError) as exc_info:
            TeamResponse(
                name="Boston Bruins",
                city="Boston",
                conference="Eastern",
                division="Atlantic",
            )
        assert "id" in str(exc_info.value)

    def test_team_response_valid(self):
        resp = TeamResponse(
            id=42,
            name="Boston Bruins",
            city="Boston",
            state="MA",
            conference="Eastern",
            division="Atlantic",
            stadium="TD Garden",
        )
        assert resp.id == 42
        assert resp.name == "Boston Bruins"

    def test_team_response_from_orm_object(self):
        entity = TeamEntity(
            name="Detroit Red Wings",
            city="Detroit",
            state="MI",
            conference="Eastern",
            division="Atlantic",
            stadium="Joe Louis Arena",
        )
        entity.id = 7

        resp = TeamResponse.model_validate(entity)
        assert resp.id == 7
        assert resp.name == "Detroit Red Wings"
        assert resp.city == "Detroit"
        assert resp.state == "MI"
        assert resp.conference == "Eastern"
        assert resp.division == "Atlantic"
        assert resp.stadium == "Joe Louis Arena"

    def test_team_response_from_orm_object_nullable_fields(self):
        entity = TeamEntity(
            name="Winnipeg Jets",
            city="Winnipeg",
            state=None,
            conference="Western",
            division="Central",
            stadium=None,
        )
        entity.id = 9

        resp = TeamResponse.model_validate(entity)
        assert resp.id == 9
        assert resp.state is None
        assert resp.stadium is None
