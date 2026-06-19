from .team_model import Team
from nest.core import Injectable


@Injectable
class TeamService:

    def __init__(self):
        self.database = []
        
    def get_team(self):
        return self.database
    
    def add_team(self, team: Team):
        self.database.append(team)
        return team
