"""
Unit tests for the SQLAlchemy ORM model (TeamEntity).
Validates column definitions, nullable constraints, __tablename__, and __repr__.
No database connection is required.
"""
import pytest
from sqlalchemy import inspect as sa_inspect

from src.modules.team.team_entity import TeamEntity


class TestTeamEntityInstantiation:

    def test_entity_creation_all_fields(self):
        entity = TeamEntity(
            name="Tampa Bay Lightning",
            city="Tampa",
            state="FL",
            conference="Eastern",
            division="Atlantic",
            stadium="Amalie Arena",
        )
        assert entity.name == "Tampa Bay Lightning"
        assert entity.city == "Tampa"
        assert entity.state == "FL"
        assert entity.conference == "Eastern"
        assert entity.division == "Atlantic"
        assert entity.stadium == "Amalie Arena"

    def test_entity_creation_nullable_fields_omitted(self):
        entity = TeamEntity(
            name="Montreal Canadiens",
            city="Montreal",
            conference="Eastern",
            division="Atlantic",
        )
        assert entity.name == "Montreal Canadiens"
        assert entity.state is None
        assert entity.stadium is None

    def test_entity_creation_nullable_state(self):
        entity = TeamEntity(
            name="Washington Capitals",
            city="Washington",
            state=None,
            conference="Eastern",
            division="Metropolitan",
            stadium="Capital One Arena",
        )
        assert entity.state is None

    def test_entity_creation_nullable_stadium(self):
        entity = TeamEntity(
            name="Ottawa Senators",
            city="Ottawa",
            state="ON",
            conference="Eastern",
            division="Atlantic",
            stadium=None,
        )
        assert entity.stadium is None

    def test_entity_id_not_set_without_db(self):
        entity = TeamEntity(
            name="Minnesota Wild",
            city="Saint Paul",
            state="MN",
            conference="Western",
            division="Central",
            stadium="Xcel Energy Center",
        )
        assert entity.id is None


class TestTeamEntityTableDefinition:

    def test_tablename(self):
        assert TeamEntity.__tablename__ == "teams"

    def test_id_column_is_primary_key(self):
        mapper = sa_inspect(TeamEntity)
        pk_cols = [col.name for col in mapper.primary_key]
        assert "id" in pk_cols

    def test_name_column_is_unique_and_indexed(self):
        mapper = sa_inspect(TeamEntity)
        name_col = next(c for c in mapper.columns if c.name == "name")
        assert name_col.unique is True
        assert name_col.index is True

    def test_name_column_not_nullable(self):
        mapper = sa_inspect(TeamEntity)
        name_col = next(c for c in mapper.columns if c.name == "name")
        assert name_col.nullable is False

    def test_city_column_not_nullable(self):
        mapper = sa_inspect(TeamEntity)
        city_col = next(c for c in mapper.columns if c.name == "city")
        assert city_col.nullable is False

    def test_conference_column_not_nullable(self):
        mapper = sa_inspect(TeamEntity)
        conf_col = next(c for c in mapper.columns if c.name == "conference")
        assert conf_col.nullable is False

    def test_division_column_not_nullable(self):
        mapper = sa_inspect(TeamEntity)
        div_col = next(c for c in mapper.columns if c.name == "division")
        assert div_col.nullable is False

    def test_state_column_is_nullable(self):
        mapper = sa_inspect(TeamEntity)
        state_col = next(c for c in mapper.columns if c.name == "state")
        assert state_col.nullable is True

    def test_stadium_column_is_nullable(self):
        mapper = sa_inspect(TeamEntity)
        stadium_col = next(c for c in mapper.columns if c.name == "stadium")
        assert stadium_col.nullable is True

    def test_all_expected_columns_present(self):
        mapper = sa_inspect(TeamEntity)
        col_names = {col.name for col in mapper.columns}
        expected = {"id", "name", "city", "state", "conference", "division", "stadium"}
        assert expected == col_names


class TestTeamEntityRepr:

    def test_repr_contains_name(self):
        entity = TeamEntity(name="Boston Bruins", city="Boston", conference="Eastern", division="Atlantic")
        entity.id = 1
        assert "Boston Bruins" in repr(entity)

    def test_repr_contains_city(self):
        entity = TeamEntity(name="Boston Bruins", city="Boston", conference="Eastern", division="Atlantic")
        entity.id = 1
        assert "Boston" in repr(entity)

    def test_repr_contains_id(self):
        entity = TeamEntity(name="Boston Bruins", city="Boston", conference="Eastern", division="Atlantic")
        entity.id = 5
        assert "5" in repr(entity)

    def test_repr_contains_conference(self):
        entity = TeamEntity(name="Boston Bruins", city="Boston", conference="Eastern", division="Atlantic")
        entity.id = 1
        assert "Eastern" in repr(entity)

    def test_repr_contains_division(self):
        entity = TeamEntity(name="Boston Bruins", city="Boston", conference="Eastern", division="Atlantic")
        entity.id = 1
        assert "Atlantic" in repr(entity)

    def test_repr_format(self):
        entity = TeamEntity(
            name="Boston Bruins",
            city="Boston",
            state="MA",
            conference="Eastern",
            division="Atlantic",
            stadium="TD Garden",
        )
        entity.id = 1
        r = repr(entity)
        assert r.startswith("<TeamEntity(")
        assert r.endswith(")>")
