import uvicorn
from src.config.database import engine, Base

# Create SQLite database schema tables dynamically before starting the server
Base.metadata.create_all(bind=engine)

if __name__ == '__main__':
    uvicorn.run(
        'src.app_module:http_server',
        host="0.0.0.0",
        port=8000,
        reload=True
    )
