# app/websocket_manager.py
from fastapi import WebSocket
from typing import Dict, List

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        print(f'User {user_id} connected. Total connections: {len(self.active_connections[user_id])}')

    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
            print(f'User {user_id} disconnected')

    async def send_personal_message(self, message: str, user_id: int):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    print(f'Error sending message to user {user_id}: {e}')

    async def send_to_users(self, message: str, user_ids: List[int]):
        """Отправляет сообщение нескольким пользователям"""
        for user_id in user_ids:
            await self.send_personal_message(message, user_id)

    async def broadcast_to_chat(self, message: str, sender_id: int, recipient_id: int):
        """Отправляет сообщение в чат между двумя пользователями"""
        # Отправителю
        await self.send_personal_message(f"You: {message}", sender_id)
        # Получателю
        await self.send_personal_message(f"User {sender_id}: {message}", recipient_id)