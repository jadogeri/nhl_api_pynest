from nest.core import Controller, Get, Post
from .team_service import TeamService
from .team_model import Team


@Controller("team", tag="team")
class TeamController:

    def __init__(self, team_service: TeamService):
        self.team_service = team_service
    
    @Get("/")
    def get_team(self):
        return self.team_service.get_team()
        
    @Post("/")
    def add_team(self, team: Team):
        return self.team_service.add_team(team)

