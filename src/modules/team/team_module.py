from nest.core import Module
from .team_controller import TeamController
from .team_service import TeamService


@Module(
    controllers=[TeamController],
    providers=[TeamService],
    imports=[]
)   
class TeamModule:
    pass

    