from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, mapped_column, Mapped, ForeignKey
from pydantic import BaseModel
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, List

engine = create_engine('sqlite:///./message.db')

new_session = sessionmaker(engine, expire_on_commit=False)

def get_session():
    with new_session() as session:
        yield session

class Base(DeclarativeBase):
    pass

class MessageModel(Base):
    __tablename__ = 'Message'
    id: Mapped[int] = mapped_column(primary_key=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey("Users.id"))
    recipient_id: Mapped[int] = mapped_column(ForeignKey("Users.id"))
    content: Mapped[str]

class MessageShame(BaseModel):
    sender_id: int
    recipient_id: int
    content: str

class ConnectionMenager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        print(f'User {user_id} connected. Total connections {len(self.active_connections[user_id])}')

    def disconnect(self, websocket: WebSocket, user_id):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
            print(f'User {user_id} disconnected. Total connections {len(self.active_connections.get(user_id, []))}')

    async def send_personal_message(self, message:str, user_id:int):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    print(f'Error sending message to user {user_id}: {e}')

    async def broadcast(self, message: str, recipient_id: int, sender_id: int):
        # Отправляем сообщение конкретному получателю
        if recipient_id in self.active_connections:
            for connection in self.active_connections[recipient_id]:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    print(f'Error broadcasting message to {recipient_id}: {e}')
        
        # Также отправляем отправителю (чтобы он видел свое сообщение)
        if sender_id in self.active_connections:
            for connection in self.active_connections[sender_id]:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    print(f'Error sending message to sender {sender_id}: {e}')

                    