from nest.core import PyNestFactory, Module
from src.modules.team.team_module import TeamModule


@Module(imports=[TeamModule], controllers=[], providers=[])
class AppModule:
    pass


app = PyNestFactory.create(
    AppModule,
    description="This is my PyNest app.",
    title="PyNest Application",
    version="1.0.0",
    debug=True,
)
http_server = app.get_server()
