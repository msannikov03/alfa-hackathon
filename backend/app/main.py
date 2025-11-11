from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.database import init_db
from app.api.routes import router
from app.telegram.bot import setup_telegram_bot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown logic"""
    logger.info("Starting Alfa Business Assistant...")
    
    # Initialize database
    await init_db()
    
    # Setup Telegram bot
    if settings.TELEGRAM_BOT_TOKEN:
        await setup_telegram_bot()
    
    yield
    
    logger.info("Shutting down...")

app = FastAPI(
    title="Alfa Business Assistant API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}