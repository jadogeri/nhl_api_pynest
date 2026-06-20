from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from src.config.database import Base

class TeamEntity(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    city: Mapped[str] = mapped_column(String, nullable=False)
    state: Mapped[str] = mapped_column(String, nullable=False)
    conference: Mapped[str] = mapped_column(String, nullable=False)
    division: Mapped[str] = mapped_column(String, nullable=False)
    stadium: Mapped[str] = mapped_column(String, nullable=False)
