from typing import Optional
from nest.core import Controller, Get, Post, Put, Delete
from src.modules.team.team_service import TeamService
from src.modules.team.team_model import Team, TeamUpdate

@Controller("teams", tag="Teams")
class TeamController:

    def __init__(self, team_service: TeamService):
        self.team_service = team_service
    
    @Get("/")
    def read_teams(self, conference: Optional[str] = None, division: Optional[str] = None):
        return self.team_service.list_teams(conference=conference, division=division)

    @Get("/{team_id}")
    def read_team(self, team_id: int):
        return self.team_service.get_team(team_id)
        
    @Post("/")
    def add_team(self, team: Team):
        return self.team_service.add_team(team)

    @Put("/{team_id}")
    def update_existing_team(self, team_id: int, team_in: TeamUpdate):
        return self.team_service.modify_team(team_id, team_in)

    @Delete("/{team_id}")
    def delete_existing_team(self, team_id: int):
        return self.team_service.remove_team(team_id)

    @Post("/populate")
    def populate_database(self):
        return self.team_service.populate_from_file()

    @Post("/truncate")
    def truncate_database(self):
        return self.team_service.clear_all_teams()
