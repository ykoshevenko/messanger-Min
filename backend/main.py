from fastapi import FastAPI, HTTPException, Depends, APIRouter, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.auth import createAccount, login
from app.database import get_session, setup_database
from app.message_database import ConnectionMenager, MessageModel
from typing import Dict

app = FastAPI()
menager = ConnectionMenager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

class User(BaseModel):
    username: str
    password: str

@app.on_event("startup")
def on_startup():
    setup_database()
    print("Database initialized")

@app.post('/api/create_user')
def create_user(data: User, session = Depends(get_session)): 
    try:
        createAccount(data, session)  
        return {"message": "User created successfully", "status": 201}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post('/api/auth')
def authenticated(data: User, session = Depends(get_session)):  
    try:
        return login(data, session)  
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket('/ws/{sender_id}/{recipient_id}')
async def websocket(websocket: WebSocket, sender_id:int, recipient_id:int, session = Depends(get_session)):
    await menager.connect(websocket, sender_id)
    await menager.send_personal_message(f'User {sender_id} is now online')

    try:
        while True:
            data = await websocket.receive_text()
            
            message = MessageModel(
                sender_id=sender_id,
                recipient_id=recipient_id,
                content=data
            )
            session.add(message)
            session.commit()

            formatted_message = f'User {sender_id}: {data}'
            await menager.broadcast(
                message=formatted_message,
                recipient_id=recipient_id,
                sender_id=sender_id
            )
    except WebSocketDisconnect:
        menager.disconnect(websocket, sender_id)

        await menager.send_personal_message(
            f'User {sender_id} is now offline',
            recipient_id
        )