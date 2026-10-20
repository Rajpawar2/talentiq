import json
from typing import Dict, List
from fastapi import WebSocket

class ConnectionManager:
    """Manages real-time WebSocket connections per interview room."""

    def __init__(self):
        # Maps interview_id to list of active WebSockets
        self.active_rooms: Dict[str, List[WebSocket]] = {}

    async def connect(self, interview_id: str, websocket: WebSocket):
        await websocket.accept()
        if interview_id not in self.active_rooms:
            self.active_rooms[interview_id] = []
        self.active_rooms[interview_id].append(websocket)

    def disconnect(self, interview_id: str, websocket: WebSocket):
        if interview_id in self.active_rooms:
            if websocket in self.active_rooms[interview_id]:
                self.active_rooms[interview_id].remove(websocket)
            if not self.active_rooms[interview_id]:
                del self.active_rooms[interview_id]

    async def broadcast_to_room(self, interview_id: str, message: dict):
        if interview_id in self.active_rooms:
            text = json.dumps(message)
            for connection in list(self.active_rooms[interview_id]):
                try:
                    await connection.send_text(text)
                except Exception:
                    # In case of broken pipe
                    pass

ws_manager = ConnectionManager()
