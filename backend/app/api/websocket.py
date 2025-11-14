from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""

    def __init__(self):
        # Store active connections per user
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        """Accept a new WebSocket connection"""
        await websocket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = []

        self.active_connections[user_id].append(websocket)
        logger.info(f"User {user_id} connected. Total connections: {len(self.active_connections[user_id])}")

    def disconnect(self, websocket: WebSocket, user_id: int):
        """Remove a WebSocket connection"""
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
                logger.info(f"User {user_id} disconnected. Remaining: {len(self.active_connections[user_id])}")

            # Clean up if no connections left
            if len(self.active_connections[user_id]) == 0:
                del self.active_connections[user_id]

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific WebSocket"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending message: {e}")

    async def send_to_user(self, message: dict, user_id: int):
        """Send a message to all connections of a specific user"""
        if user_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending to user {user_id}: {e}")
                    disconnected.append(connection)

            # Clean up disconnected sockets
            for connection in disconnected:
                self.disconnect(connection, user_id)

    async def broadcast(self, message: dict):
        """Broadcast a message to all connected users"""
        for user_id in list(self.active_connections.keys()):
            await self.send_to_user(message, user_id)

    async def notify_action_taken(self, user_id: int, action: dict):
        """Notify user about an autonomous action"""
        message = {
            "type": "action_taken",
            "timestamp": datetime.now().isoformat(),
            "data": action,
        }
        await self.send_to_user(message, user_id)

    async def notify_approval_needed(self, user_id: int, action: dict):
        """Notify user that an action needs approval"""
        message = {
            "type": "approval_needed",
            "timestamp": datetime.now().isoformat(),
            "data": action,
        }
        await self.send_to_user(message, user_id)

    async def notify_metric_update(self, user_id: int, metric: dict):
        """Notify user about a metric update"""
        message = {
            "type": "metric_update",
            "timestamp": datetime.now().isoformat(),
            "data": metric,
        }
        await self.send_to_user(message, user_id)

    async def notify_briefing_ready(self, user_id: int, briefing: dict):
        """Notify user that briefing is ready"""
        message = {
            "type": "briefing_ready",
            "timestamp": datetime.now().isoformat(),
            "data": briefing,
        }
        await self.send_to_user(message, user_id)


# Global connection manager instance
manager = ConnectionManager()
