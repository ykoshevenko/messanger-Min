from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.auth import login, createAccount, security
from app.database import get_session, setup_database, get_all_users, MessageModel
from app.websocket_manager import ConnectionManager

app = FastAPI()
manager = ConnectionManager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserSchema(BaseModel):
    username: str
    password: str

class MessageSchema(BaseModel):
    sender_id: int
    recipient_id: int
    content: str

@app.on_event("startup")
def on_startup():
    setup_database()
    print("Database initialized")

@app.post('/api/create_user')
def create_user(data: UserSchema, session: Session = Depends(get_session)):
    try:
        user = createAccount(data, session)
        return {
            "message": "User created successfully",
            "user_id": user.id,
            "username": user.username,
            "status": 201
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post('/api/auth')
def authenticate(data: UserSchema, session: Session = Depends(get_session)):
    try:
        return login(data, session)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.get('/api/get_all_users')
def get_users(session: Session = Depends(get_session)):
    users = get_all_users(session)
    # Не возвращаем пароли
    return [{"id": user.id, "username": user.username} for user in users]

# Защищенный endpoint (пример с правильным использованием AuthX)
@app.get('/api/protected')
def protected_route(request: Request):
    # Извлекаем токен из заголовков
    token = security.extract_token(request)
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Декодируем токен
    payload = security.decode_token(token)
    user_id = payload.get("sub")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return {"message": f"Hello user {user_id}", "user_id": user_id}

# Более простой защищенный endpoint с использованием dependency
@app.get('/api/me')
def get_current_user(request: Request):
    # Проверяем аутентификацию
    user = security.get_authenticated_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return {"user_id": user, "message": "Authenticated"}

@app.websocket('/ws/{user_id}')
async def websocket_endpoint(
    websocket: WebSocket, 
    user_id: int,
    session: Session = Depends(get_session)
):
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            # Ожидаем сообщение в формате JSON
            data = await websocket.receive_json()
            
            # Проверяем структуру сообщения
            if 'recipient_id' not in data or 'content' not in data:
                await manager.send_personal_message(
                    "Error: Invalid message format. Required fields: recipient_id, content", 
                    user_id
                )
                continue
            
            recipient_id = data['recipient_id']
            content = data['content']
            
            # Сохраняем сообщение в БД
            message = MessageModel(
                sender_id=user_id,
                recipient_id=recipient_id,
                content=content
            )
            
            session.add(message)
            session.commit()
            session.refresh(message)
            
            # Отправляем сообщение получателю
            await manager.send_personal_message(
                f"User {user_id}: {content}",
                recipient_id
            )
            
            # Подтверждение отправителю
            await manager.send_personal_message(
                f"Message sent to user {recipient_id}",
                user_id
            )
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
        print(f"User {user_id} disconnected")

@app.get('/api/messages/{user_id}/{other_user_id}')
def get_chat_messages(
    user_id: int, 
    other_user_id: int,
    session: Session = Depends(get_session)
):
    """Получение истории переписки между двумя пользователями"""
    messages = session.query(MessageModel).filter(
        ((MessageModel.sender_id == user_id) & (MessageModel.recipient_id == other_user_id)) |
        ((MessageModel.sender_id == other_user_id) & (MessageModel.recipient_id == user_id))
    ).order_by(MessageModel.timestamp).all()
    
    return [
        {
            "id": msg.id,
            "sender_id": msg.sender_id,
            "recipient_id": msg.recipient_id,
            "content": msg.content,
            "timestamp": msg.timestamp.isoformat() if msg.timestamp else None
        }
        for msg in messages
    ]

# Endpoint для отправки сообщений через HTTP (альтернатива WebSocket)
@app.post('/api/send_message')
async def send_message(
    data: MessageSchema,
    session: Session = Depends(get_session)
):
    """Отправка сообщения через HTTP (полезно для отладки)"""
    
    message = MessageModel(
        sender_id=data.sender_id,
        recipient_id=data.recipient_id,
        content=data.content
    )
    
    session.add(message)
    session.commit()
    session.refresh(message)
    
    # Отправляем через WebSocket, если получатель онлайн
    await manager.send_personal_message(
        f"User {data.sender_id}: {data.content}",
        data.recipient_id
    )
    
    return {
        "status": "Message sent",
        "message_id": message.id
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)