"""
Unit tests for TeamRepository.
The SQLAlchemy session is fully mocked — no real database is used.

Each repository method opens a `with self.session_factory() as db:` block.
We override `repository.session_factory` with a MagicMock whose context manager
returns a mock db session, giving us full control over query return values.
"""
import pytest
from unittest.mock import MagicMock, patch, call

from src.modules.team.team_repository import TeamRepository
from src.modules.team.team_entity import TeamEntity
from src.modules.team.team_model import Team, TeamUpdate


def make_mock_session():
    """Return (mock_db, mock_session_factory) pair.

    mock_session_factory() returns a context manager whose __enter__ yields mock_db.
    Assign to repository.session_factory to intercept all DB calls.
    """
    mock_db = MagicMock()
    mock_cm = MagicMock()
    mock_cm.__enter__ = MagicMock(return_value=mock_db)
    mock_cm.__exit__ = MagicMock(return_value=False)
    mock_factory = MagicMock(return_value=mock_cm)
    return mock_db, mock_factory


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
def repo():
    repository = TeamRepository()
    return repository


class TestGetAllTeams:

    def test_get_all_teams_no_filter(self, repo):
        mock_db, mock_factory = make_mock_session()
        repo.session_factory = mock_factory
        expected = [make_team_entity(1), make_team_entity(2, name="Buffalo Sabres", city="Buffalo")]
        mock_db.query.return_value.all.return_value = expected

        result = repo.get_all_teams()

        mock_db.query.assert_called_once_with(TeamEntity)
        assert result == expected

    def test_get_all_teams_conference_filter(self, repo):
        mock_db, mock_factory = make_mock_session()
        repo.session_factory = mock_factory
        query_mock = MagicMock()
        mock_db.query.return_value = query_mock
        filtered_mock = MagicMock()
        query_mock.filter.return_value = filtered_mock
        filtered_mock.all.return_value = [make_team_entity()]

        result = repo.get_all_teams(conference="Eastern")

        query_mock.filter.assert_called_once()
        assert len(result) == 1

    def test_get_all_teams_division_filter(self, repo):
        mock_db, mock_factory = make_mock_session()
        repo.session_factory = mock_factory
        query_mock = MagicMock()
        mock_db.query.return_value = query_mock
        filtered_mock = MagicMock()
        query_mock.filter.return_value = filtered_mock
        filtered_mock.all.return_value = [make_team_entity()]

        result = repo.get_all_teams(division="Atlantic")

        query_mock.filter.assert_called_once()
        assert result is not None

    def test_get_all_teams_both_filters(self, repo):
        mock_db, mock_factory = make_mock_session()
        repo.session_factory = mock_factory
        query_mock = MagicMock()
        mock_db.query.return_value = query_mock
        first_filter_mock = MagicMock()
        second_filter_mock = MagicMock()
        query_mock.filter.return_value = first_filter_mock
        first_filter_mock.filter.return_value = second_filter_mock
        second_filter_mock.all.return_value = [make_team_entity()]

        result = repo.get_all_teams(conference="Eastern", division="Atlantic")

        assert query_mock.filter.call_count == 1
        assert first_filter_mock.filter.call_count == 1

    def test_get_all_teams_returns_empty_list(self, repo):
        mock_db, mock_factory = make_mock_session()
        repo.session_factory = mock_factory
        mock_db.query.return_value.all.return_value = []

        result = repo.get_all_teams()

        assert result == []


class TestGetTeamById:

    def test_get_team_by_id_found(self, repo):
        mock_db, mock_factory = make_mock_session()
        repo.session_factory = mock_factory
        expected = make_team_entity(id=3)
        mock_db.query.return_value.filter.return_value.first.return_value = expected

        result = repo.get_team_by_id(3)

        assert result == expected

    def test_get_team_by_id_not_found(self, repo):
        mock_db, mock_factory = make_mock_session()
        repo.session_factory = mock_factory
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = repo.get_team_by_id(999)

        assert result is None

    def test_get_team_by_id_queries_team_entity(self, repo):
        mock_db, mock_factory = make_mock_session()
        repo.session_factory = mock_factory
        mock_db.query.return_value.filter.return_value.first.return_value = None

        repo.get_team_by_id(1)

        mock_db.query.assert_called_once_with(TeamEntity)


class TestGetTeamByName:

    def test_get_team_by_name_found(self, repo):
        mock_db, mock_factory = make_mock_session()
        repo.session_factory = mock_factory
        expected = make_team_entity(name="Boston Bruins")
        mock_db.query.return_value.filter.return_value.first.return_value = expected

        result = repo.get_team_by_name("Boston Bruins")

        assert result == expected

    def test_get_team_by_name_not_found(self, repo):
        mock_db, mock_factory = make_mock_session()
        repo.session_factory = mock_factory
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = repo.get_team_by_name("Nonexistent Team")

        assert result is None


class TestCreateTeam:

    def test_create_team_adds_and_commits(self, repo):
        mock_db, mock_factory = make_mock_session()
        repo.session_factory = mock_factory

        team_data = Team(
            name="Vegas Golden Knights",
            city="Las Vegas",
            state="NV",
            conference="Western",
            division="Pacific",
            stadium="T-Mobile Arena",
        )

        created_entity = make_team_entity(
            id=30,
            name="Vegas Golden Knights",
            city="Las Vegas",
            state="NV",
            conference="Western",
            division="Pacific",
            stadium="T-Mobile Arena",
        )
        mock_db.refresh.side_effect = lambda e: None

        def add_side_effect(entity):
            entity.id = 30

        mock_db.add.side_effect = add_side_effect
        mock_db.refresh.side_effect = lambda e: setattr(e, "id", 30)

        result = repo.create_team(team_data)

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_create_team_returns_entity(self, repo):
        mock_db, mock_factory = make_mock_session()
        repo.session_factory = mock_factory

        team_data = Team(
            name="Seattle Kraken",
            city="Seattle",
            state="WA",
            conference="Western",
            division="Pacific",
        )

        result = repo.create_team(team_data)

        assert isinstance(result, TeamEntity)
        assert result.name == "Seattle Kraken"


class TestUpdateTeam:

    def test_update_team_merges_and_commits(self, repo):
        mock_db, mock_factory = make_mock_session()
        repo.session_factory = mock_factory

        original = make_team_entity(id=1, stadium="Old Arena")
        merged_entity = make_team_entity(id=1, stadium="Old Arena")
        mock_db.merge.return_value = merged_entity

        update = TeamUpdate(stadium="New Arena")

        result = repo.update_team(original, update)

        mock_db.merge.assert_called_once_with(original)
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(merged_entity)

    def test_update_team_applies_partial_update(self, repo):
        mock_db, mock_factory = make_mock_session()
        repo.session_factory = mock_factory

        original = make_team_entity(id=1, stadium="Old Arena", city="Boston")
        merged_entity = make_team_entity(id=1, stadium="Old Arena", city="Boston")
        mock_db.merge.return_value = merged_entity

        update = TeamUpdate(stadium="New Arena")

        repo.update_team(original, update)

        assert merged_entity.stadium == "New Arena"
        assert merged_entity.city == "Boston"

    def test_update_team_exclude_unset_fields(self, repo):
        mock_db, mock_factory = make_mock_session()
        repo.session_factory = mock_factory

        original = make_team_entity(id=1, name="Boston Bruins")
        merged_entity = make_team_entity(id=1, name="Boston Bruins")
        mock_db.merge.return_value = merged_entity

        update = TeamUpdate(city="New City")

        repo.update_team(original, update)

        assert merged_entity.name == "Boston Bruins"
        assert merged_entity.city == "New City"


class TestDeleteTeam:

    def test_delete_team_merges_deletes_and_commits(self, repo):
        mock_db, mock_factory = make_mock_session()
        repo.session_factory = mock_factory

        entity = make_team_entity(id=1)
        merged_entity = make_team_entity(id=1)
        mock_db.merge.return_value = merged_entity

        repo.delete_team(entity)

        mock_db.merge.assert_called_once_with(entity)
        mock_db.delete.assert_called_once_with(merged_entity)
        mock_db.commit.assert_called_once()

    def test_delete_team_returns_none(self, repo):
        mock_db, mock_factory = make_mock_session()
        repo.session_factory = mock_factory

        entity = make_team_entity(id=1)
        mock_db.merge.return_value = entity

        result = repo.delete_team(entity)

        assert result is None


class TestTruncateTeams:

    def test_truncate_teams_deletes_all_and_commits(self, repo):
        mock_db, mock_factory = make_mock_session()
        repo.session_factory = mock_factory
        mock_db.query.return_value.delete.return_value = 30

        repo.truncate_teams()

        mock_db.query.assert_called_once_with(TeamEntity)
        mock_db.query.return_value.delete.assert_called_once()
        mock_db.commit.assert_called_once()

    def test_truncate_teams_returns_none(self, repo):
        mock_db, mock_factory = make_mock_session()
        repo.session_factory = mock_factory

        result = repo.truncate_teams()

        assert result is None
