import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_nhl.db")

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config.database import Base
from src.modules.team.team_entity import TeamEntity
from src.modules.team.team_model import Team, TeamUpdate, TeamResponse

TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_session(test_engine):
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )
    session = TestingSessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def test_session_factory(test_engine):
    return sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )


@pytest.fixture
def sample_team_data():
    return {
        "name": "Boston Bruins",
        "city": "Boston",
        "state": "MA",
        "conference": "Eastern",
        "division": "Atlantic",
        "stadium": "TD Garden",
    }


@pytest.fixture
def sample_team(sample_team_data):
    return Team(**sample_team_data)


@pytest.fixture
def sample_team_entity(sample_team_data):
    entity = TeamEntity(**sample_team_data)
    entity.id = 1
    return entity


@pytest.fixture
def sample_team_response(sample_team_data):
    return TeamResponse(id=1, **sample_team_data)
