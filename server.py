from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from app.config.env_config import Config
from app.config.db_connection import connect_database, get_database, disconnect_database
from app.routes.product_routes import router as product_router
from app.routes.order_routes import router as order_router
from app.routes.ai_routes import router as ai_router

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

# Include routers
app.include_router(product_router)
app.include_router(order_router)
app.include_router(ai_router)

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
    return {
        "status": "healthy",
        "database": "connected" if get_database() else "disconnected"
    }

if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )