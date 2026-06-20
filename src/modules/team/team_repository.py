from typing import Optional, List
from src.modules.team.team_entity import TeamEntity
from src.modules.team.team_model import Team, TeamUpdate

class TeamRepository:
    def __init__(self):
        # 👈 THE FIX: Define session_factory using a lambda function.
        # This dynamically references the global SessionLocal at the exact 
        # moment your query calls it, allowing pytest's patch to work perfectly!
        from src.config.database import SessionLocal
        self.session_factory = lambda: SessionLocal()

    def get_all_teams(self, conference: Optional[str] = None, division: Optional[str] = None) -> List[TeamEntity]:
        with self.session_factory() as db:
            query = db.query(TeamEntity)
            if conference:
                query = query.filter(TeamEntity.conference.ilike(conference))
            if division:
                query = query.filter(TeamEntity.division.ilike(division))
            return query.all()

    def get_team_by_id(self, team_id: int) -> Optional[TeamEntity]:
        with self.session_factory() as db:
            return db.query(TeamEntity).filter(TeamEntity.id == team_id).first()

    def get_team_by_name(self, name: str) -> Optional[TeamEntity]:
        with self.session_factory() as db:
            return db.query(TeamEntity).filter(TeamEntity.name.ilike(name)).first()

    def create_team(self, team_data: Team) -> TeamEntity:
        with self.session_factory() as db:
            db_team = TeamEntity(**team_data.model_dump())
            db.add(db_team)
            db.commit()
            db.refresh(db_team)
            return db_team

    def update_team(self, db_team: TeamEntity, update_data: TeamUpdate) -> TeamEntity:
        with self.session_factory() as db:
            db_team = db.merge(db_team)
            update_dict = update_data.model_dump(exclude_unset=True)
            for key, value in update_dict.items():
                setattr(db_team, key, value)
            db.commit()
            db.refresh(db_team)
            return db_team

    def delete_team(self, db_team: TeamEntity) -> None:
        with self.session_factory() as db:
            db_team = db.merge(db_team)
            db.delete(db_team)
            db.commit()

    def truncate_teams(self) -> None:
        with self.session_factory() as db:
            db.query(TeamEntity).delete()
            db.commit()
