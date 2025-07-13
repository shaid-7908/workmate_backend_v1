from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from app.config.env_config import Config
from app.config.db_connection import connect_database, get_database, disconnect_database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
config = Config()

@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Lifespan event handler for startup and shutdown."""
    # Startup
    logger.info("🚀 Starting Workmate Backend API...")
    
    # Connect to database
    if connect_database():
        logger.info("✅ Database connected successfully")
    else:
        logger.error("❌ Failed to connect to database")
        raise Exception("Database connection failed")
    
    yield
    
    # Shutdown
    logger.info("🔄 Shutting down Workmate Backend API...")
    disconnect_database()
    logger.info("✅ Database disconnected")

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Workmate Backend API",
    description="Backend API for Workmate application",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Workmate Backend API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        db = get_database()
        if db is not None:
            # Test database connection
            _ = db.command("ping")
            return {
                "status": "healthy",
                "database": "connected",
                "message": "API and database are running"
            }
        else:
            return {
                "status": "unhealthy",
                "database": "disconnected",
                "message": "Database not connected"
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "error",
            "message": f"Database error: {str(e)}"
        }

@app.get("/api/test")
async def test_endpoint():
    """Test endpoint to verify API is working."""
    return {
        "message": "API is working!",
        "timestamp": "2024-01-01T00:00:00Z"
    }

if __name__ == "__main__":
    # Get port from config, default to 8000
    port = int(config.PORT) if config.PORT else 8000
    
    logger.info(f"🌐 Starting server on port {port}")
    
    # Run the FastAPI app with uvicorn
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=port,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )