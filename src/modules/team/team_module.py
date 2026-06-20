from nest.core import Module
from .team_controller import TeamController
from .team_service import TeamService
from .team_repository import TeamRepository

# Explicit factory function to map out the dependency tracking context manually
def team_service_factory(repository: TeamRepository) -> TeamService:
    return TeamService(repository)

@Module(
    controllers=[TeamController],
    providers=[
        TeamRepository,
        {
            "provide": TeamService,
            "useFactory": team_service_factory,  # 👈 MUST be camelCase 'useFactory' for PyNest
            "inject": [TeamRepository]
        }
    ],
    imports=[]
)   
class TeamModule:
    pass
