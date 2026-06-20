import json
import os
from typing import Optional, List, Dict, Any
from fastapi import HTTPException

from src.modules.team.team_repository import TeamRepository
from src.modules.team.team_model import Team, TeamUpdate, TeamResponse

class TeamService:
    def __init__(self, repository: TeamRepository):
        self.repository = repository

    def list_teams(self, conference: Optional[str] = None, division: Optional[str] = None) -> List[TeamResponse]:
        teams = self.repository.get_all_teams(conference, division)
        return [TeamResponse.model_validate(t) for t in teams]

    def get_team(self, team_id: int) -> TeamResponse:
        team = self.repository.get_team_by_id(team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        return TeamResponse.model_validate(team)

    def add_team(self, team_data: Team) -> TeamResponse:
        existing = self.repository.get_team_by_name(team_data.name)
        if existing:
            raise HTTPException(status_code=400, detail=f"Team '{team_data.name}' already exists.")
        new_team = self.repository.create_team(team_data)
        return TeamResponse.model_validate(new_team)

    def modify_team(self, team_id: int, update_data: TeamUpdate) -> TeamResponse:
        db_team = self.repository.get_team_by_id(team_id)
        if not db_team:
            raise HTTPException(status_code=404, detail="Team not found")
        updated = self.repository.update_team(db_team, update_data)
        return TeamResponse.model_validate(updated)

    def remove_team(self, team_id: int) -> Dict[str, str]:
        db_team = self.repository.get_team_by_id(team_id)
        if not db_team:
            raise HTTPException(status_code=404, detail="Team not found")
        self.repository.delete_team(db_team)
        return {"message": "Team deleted successfully"}

    def populate_from_file(self, file_path: str = "nhl_teams.json") -> Dict[str, Any]:
        if not os.path.exists(file_path):
            raise HTTPException(status_code=500, detail=f"Source file '{file_path}' not found.")
        
        with open(file_path, "r") as f:
            data = json.load(f)

        count = 0
        for team_raw in data.get("nhl_teams", []):
            existing = self.repository.get_team_by_name(team_raw["name"])
            if not existing:
                team_schema = Team(**team_raw)
                self.repository.create_team(team_schema)
                count += 1
        return {"message": f"Populated successfully. Added {count} unique teams."}

    def clear_all_teams(self) -> Dict[str, str]:
        self.repository.truncate_teams()
        return {"message": "All team database records dropped successfully."}
