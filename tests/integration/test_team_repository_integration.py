"""
Integration tests for TeamRepository.
Uses a real in-memory SQLite database. No mocking — all reads and writes
go through SQLAlchemy against an actual database engine.

The session_factory on each repository instance is replaced with
a test factory pointing at the in-memory engine.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config.database import Base
from src.modules.team.team_repository import TeamRepository
from src.modules.team.team_entity import TeamEntity
from src.modules.team.team_model import Team, TeamUpdate


TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="module")
def engine():
    eng = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=eng)
    yield eng
    Base.metadata.drop_all(bind=eng)


@pytest.fixture(scope="function")
def session_factory(engine):
    factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return factory


@pytest.fixture(scope="function")
def repo(session_factory, engine):
    repository = TeamRepository()
    repository.session_factory = session_factory
    yield repository
    # Truncate teams table between tests for isolation
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
        name=name,
        city=city,
        state=state,
        conference=conference,
        division=division,
        stadium=stadium,
    )


class TestGetAllTeamsIntegration:

    def test_get_all_teams_empty_database(self, repo):
        result = repo.get_all_teams()
        assert result == []

    def test_get_all_teams_returns_all_records(self, repo):
        repo.create_team(make_team("Boston Bruins", "Boston", "MA", "Eastern", "Atlantic"))
        repo.create_team(make_team("Buffalo Sabres", "Buffalo", "NY", "Eastern", "Atlantic"))

        result = repo.get_all_teams()

        assert len(result) == 2

    def test_get_all_teams_conference_filter(self, repo):
        repo.create_team(make_team("Boston Bruins", "Boston", "MA", "Eastern", "Atlantic"))
        repo.create_team(make_team("Chicago Blackhawks", "Chicago", "IL", "Western", "Central"))

        result = repo.get_all_teams(conference="Eastern")

        assert len(result) == 1
        assert result[0].name == "Boston Bruins"

    def test_get_all_teams_conference_filter_case_insensitive(self, repo):
        repo.create_team(make_team("Boston Bruins", "Boston", "MA", "Eastern", "Atlantic"))

        result = repo.get_all_teams(conference="eastern")

        assert len(result) == 1

    def test_get_all_teams_division_filter(self, repo):
        repo.create_team(make_team("Boston Bruins", "Boston", "MA", "Eastern", "Atlantic"))
        repo.create_team(make_team("Pittsburgh Penguins", "Pittsburgh", "PA", "Eastern", "Metropolitan", "PPG Paints Arena"))

        result = repo.get_all_teams(division="Atlantic")

        assert len(result) == 1
        assert result[0].name == "Boston Bruins"

    def test_get_all_teams_both_filters(self, repo):
        repo.create_team(make_team("Boston Bruins", "Boston", "MA", "Eastern", "Atlantic"))
        repo.create_team(make_team("Tampa Bay Lightning", "Tampa", "FL", "Eastern", "Atlantic", "Amalie Arena"))
        repo.create_team(make_team("Chicago Blackhawks", "Chicago", "IL", "Western", "Central"))

        result = repo.get_all_teams(conference="Eastern", division="Atlantic")

        assert len(result) == 2

    def test_get_all_teams_no_match_returns_empty(self, repo):
        repo.create_team(make_team())

        result = repo.get_all_teams(conference="Western")

        assert result == []


class TestGetTeamByIdIntegration:

    def test_get_team_by_id_found(self, repo):
        created = repo.create_team(make_team())

        result = repo.get_team_by_id(created.id)

        assert result is not None
        assert result.id == created.id
        assert result.name == "Boston Bruins"

    def test_get_team_by_id_not_found(self, repo):
        result = repo.get_team_by_id(99999)

        assert result is None

    def test_get_team_by_id_returns_correct_entity(self, repo):
        repo.create_team(make_team("Boston Bruins", "Boston", "MA", "Eastern", "Atlantic"))
        second = repo.create_team(make_team("Buffalo Sabres", "Buffalo", "NY", "Eastern", "Atlantic"))

        result = repo.get_team_by_id(second.id)

        assert result.name == "Buffalo Sabres"


class TestGetTeamByNameIntegration:

    def test_get_team_by_name_found(self, repo):
        repo.create_team(make_team("Boston Bruins"))

        result = repo.get_team_by_name("Boston Bruins")

        assert result is not None
        assert result.name == "Boston Bruins"

    def test_get_team_by_name_not_found(self, repo):
        result = repo.get_team_by_name("Nonexistent Team")

        assert result is None

    def test_get_team_by_name_case_insensitive(self, repo):
        repo.create_team(make_team("Boston Bruins"))

        result = repo.get_team_by_name("boston bruins")

        assert result is not None


class TestCreateTeamIntegration:

    def test_create_team_persists_to_database(self, repo):
        team_data = make_team()

        created = repo.create_team(team_data)

        fetched = repo.get_team_by_id(created.id)
        assert fetched is not None
        assert fetched.name == "Boston Bruins"

    def test_create_team_assigns_id(self, repo):
        created = repo.create_team(make_team())

        assert created.id is not None
        assert isinstance(created.id, int)

    def test_create_team_stores_all_fields(self, repo):
        team_data = make_team(
            name="Detroit Red Wings",
            city="Detroit",
            state="MI",
            conference="Eastern",
            division="Atlantic",
            stadium="Joe Louis Arena",
        )

        created = repo.create_team(team_data)

        assert created.name == "Detroit Red Wings"
        assert created.city == "Detroit"
        assert created.state == "MI"
        assert created.conference == "Eastern"
        assert created.division == "Atlantic"
        assert created.stadium == "Joe Louis Arena"

    def test_create_team_with_nullable_fields(self, repo):
        team_data = Team(
            name="Winnipeg Jets",
            city="Winnipeg",
            conference="Western",
            division="Central",
        )

        created = repo.create_team(team_data)

        assert created.state is None
        assert created.stadium is None

    def test_create_multiple_teams_have_unique_ids(self, repo):
        first = repo.create_team(make_team("Boston Bruins", "Boston", "MA", "Eastern", "Atlantic"))
        second = repo.create_team(make_team("Buffalo Sabres", "Buffalo", "NY", "Eastern", "Atlantic"))

        assert first.id != second.id


class TestUpdateTeamIntegration:

    def test_update_team_persists_change(self, repo):
        created = repo.create_team(make_team(stadium="Old Arena"))
        update = TeamUpdate(stadium="New Arena")

        updated = repo.update_team(created, update)

        fetched = repo.get_team_by_id(updated.id)
        assert fetched.stadium == "New Arena"

    def test_update_team_partial_update_leaves_other_fields(self, repo):
        created = repo.create_team(make_team("Boston Bruins", "Boston", "MA", "Eastern", "Atlantic"))
        update = TeamUpdate(stadium="Updated Arena")

        updated = repo.update_team(created, update)

        assert updated.name == "Boston Bruins"
        assert updated.city == "Boston"
        assert updated.stadium == "Updated Arena"

    def test_update_team_multiple_fields(self, repo):
        created = repo.create_team(make_team())
        update = TeamUpdate(city="New City", stadium="New Stadium")

        updated = repo.update_team(created, update)

        assert updated.city == "New City"
        assert updated.stadium == "New Stadium"

    def test_update_team_empty_update_no_change(self, repo):
        created = repo.create_team(make_team("Boston Bruins", "Boston", "MA", "Eastern", "Atlantic"))
        original_name = created.name
        update = TeamUpdate()

        updated = repo.update_team(created, update)

        assert updated.name == original_name


class TestDeleteTeamIntegration:

    def test_delete_team_removes_from_database(self, repo):
        created = repo.create_team(make_team())

        repo.delete_team(created)

        result = repo.get_team_by_id(created.id)
        assert result is None

    def test_delete_team_does_not_affect_other_teams(self, repo):
        first = repo.create_team(make_team("Boston Bruins", "Boston", "MA", "Eastern", "Atlantic"))
        second = repo.create_team(make_team("Buffalo Sabres", "Buffalo", "NY", "Eastern", "Atlantic"))

        repo.delete_team(first)

        assert repo.get_team_by_id(first.id) is None
        assert repo.get_team_by_id(second.id) is not None


class TestTruncateTeamsIntegration:

    def test_truncate_clears_all_records(self, repo):
        repo.create_team(make_team("Boston Bruins", "Boston", "MA", "Eastern", "Atlantic"))
        repo.create_team(make_team("Buffalo Sabres", "Buffalo", "NY", "Eastern", "Atlantic"))

        repo.truncate_teams()

        result = repo.get_all_teams()
        assert result == []

    def test_truncate_empty_table_is_safe(self, repo):
        repo.truncate_teams()

        result = repo.get_all_teams()
        assert result == []

    def test_can_create_after_truncate(self, repo):
        repo.create_team(make_team())
        repo.truncate_teams()

        new_team = repo.create_team(make_team("Buffalo Sabres", "Buffalo", "NY", "Eastern", "Atlantic"))

        assert new_team.id is not None
        assert new_team.name == "Buffalo Sabres"
