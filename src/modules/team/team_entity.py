from sqlalchemy import Column, Integer, String
from src.config.database import Base

class TeamEntity(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=True)       # 👈 Changed nullable to True
    conference = Column(String, nullable=False)
    division = Column(String, nullable=False)
    stadium = Column(String, nullable=True)     # 👈 Changed nullable to True
    def __repr__(self):
        return f"<TeamEntity(id={self.id}, name='{self.name}', city='{self.city}', state='{self.state}', conference='{self.conference}', division='{self.division}', stadium='{self.stadium}')>"