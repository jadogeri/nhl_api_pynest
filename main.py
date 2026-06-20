import uvicorn
import asyncio
from src.config.database import engine, Base, SessionLocal
from src.modules.team.team_entity import TeamEntity
from src.app_module import app

# 1. Build database tables synchronously before starting the application
Base.metadata.create_all(bind=engine)

# 2. Automatically load data from the JSON file if the database table is empty
def auto_seed_database():
    with SessionLocal() as db:
        # Check if any teams already exist in the database table
        has_teams = db.query(TeamEntity).first() is not None
        
        if not has_teams:
            print("🚀 Database is empty! Auto-populating NHL teams from JSON...")
            from src.modules.team.team_repository import TeamRepository
            from src.modules.team.team_service import TeamService
            
            try:
                # Manually instantiate the layer context to avoid PyNest wrapper limitations
                repo = TeamRepository()
                team_service = TeamService(repository=repo)
                
                # Execute the asynchronous population function safely
                asyncio.run(team_service.populate_from_file())
                print("✅ Auto-population completed successfully.")
            except Exception as e:
                print(f"❌ Failed to auto-populate database: {e}")
        else:
            print("📦 Database already contains records. Skipping auto-population.")

# Execute the seeding check
auto_seed_database()

# 3. Extract the actual FastAPI server instance from PyNest
http_server = app.get_server()

if __name__ == "__main__":
    uvicorn.run("main:http_server", host="0.0.0.0", port=8000, reload=True)

