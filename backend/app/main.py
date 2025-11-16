from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.config import settings
from app.database import init_db
from app.api.routes import router
from app.api.auth import router as auth_router
from app.api.competitors import router as competitors_router
from app.api.legal import router as legal_router
from app.api.finance import router as finance_router
from app.api.trends import router as trends_router
from app.telegram.bot import setup_telegram_bot
from app.agents.briefing_agent import briefing_agent
from app.services.legal_service import legal_service
from app.database import AsyncSession, engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global scheduler
scheduler = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown logic"""
    global scheduler

    logger.info("Starting Alfa Business Assistant...")

    # Initialize database
    await init_db()

    # Setup Telegram bot
    if settings.TELEGRAM_BOT_TOKEN:
        await setup_telegram_bot()

    # Setup scheduler for autonomous features
    if settings.ENABLE_AUTONOMOUS_ACTIONS:
        scheduler = AsyncIOScheduler()

        # Schedule morning briefing
        hour, minute = settings.MORNING_BRIEFING_TIME.split(":")
        scheduler.add_job(
            briefing_agent.generate_all_briefings,
            CronTrigger(hour=int(hour), minute=int(minute)),
            id="morning_briefing",
            name="Generate morning briefings",
        )

        # Schedule daily legal scan
        async def run_daily_scan():
            async with AsyncSession(engine) as session:
                await legal_service.daily_scan_and_process(session)

        scheduler.add_job(
            run_daily_scan,
            CronTrigger(hour=5, minute=0), # Run every day at 5 AM
            id="daily_legal_scan",
            name="Scan for new legal updates daily",
        )

        scheduler.start()
        logger.info(f"Scheduler started - Morning briefings at {settings.MORNING_BRIEFING_TIME}, Daily legal scan at 5:00")

    yield

    # Shutdown scheduler
    if scheduler:
        scheduler.shutdown()

    logger.info("Shutting down...")

app = FastAPI(
    title="Alfa Business Assistant API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
# Get allowed origins from environment variable
cors_origins = os.getenv(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:8000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api")
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(competitors_router, prefix="/api/competitors", tags=["competitors"])
app.include_router(legal_router, prefix="/api/legal", tags=["legal"])
app.include_router(finance_router, prefix="/api/finance", tags=["finance"])
app.include_router(trends_router, prefix="/api/trends", tags=["trends"])


# WebSocket endpoint
from fastapi import WebSocket, WebSocketDisconnect
from app.api.websocket import manager

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket, user_id)
    try:
        while True:
            # Wait for messages from client
            data = await websocket.receive_text()

            # Echo back for heartbeat/ping
            await websocket.send_json({
                "type": "pong",
                "timestamp": "2024-01-01T00:00:00"  # Would use real timestamp
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
        logger.info(f"WebSocket disconnected for user {user_id}")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}