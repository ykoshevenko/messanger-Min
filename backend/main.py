from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.auth import login, createAccount, security
from app.database import get_session, setup_database, get_all_users, MessageModel
from app.websocket_manager import ConnectionManager

app = FastAPI()
manager = ConnectionManager()

# Улучшенные настройки CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Явно укажите фронтенд URL
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
    expose_headers=["Authorization"],
    max_age=600,  # 10 минут кэширования preflight
)

# Удалите или закомментируйте ваш AuthMiddleware
# app.add_middleware(AuthMiddleware)

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

# Общедоступные эндпоинты
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

# Защищенные эндпоинты (требуют авторизации)
@app.get('/api/get_all_users')
def get_users(
    request: Request,
    session: Session = Depends(get_session)
):
    # Проверяем авторизацию
    user_id = security.get_authenticated_user(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    users = get_all_users(session)
    # Не возвращаем пароли и текущего пользователя
    return [
        {"id": user.id, "username": user.username} 
        for user in users 
        if user.id != int(user_id)
    ]

# Эндпоинт для проверки авторизации - ОБНОВЛЕННЫЙ
@app.api_route('/api/check_auth', methods=['GET', 'OPTIONS'])
def check_auth(request: Request):
    # Для OPTIONS запросов возвращаем пустой ответ с заголовками
    if request.method == "OPTIONS":
        from fastapi.responses import Response
        return Response(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "http://localhost:3000",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "Authorization, Content-Type",
                "Access-Control-Allow-Credentials": "true",
            }
        )
    
    # Для GET запросов проверяем авторизацию
    try:
        user_id = security.get_authenticated_user(request)
        if user_id:
            return {
                "authenticated": True, 
                "user_id": user_id,
                "message": "User is authenticated"
            }
        return {
            "authenticated": False,
            "message": "User is not authenticated"
        }
    except Exception as e:
        # Логируем ошибку но не падаем
        print(f"Error in check_auth: {e}")
        return {
            "authenticated": False,
            "error": str(e)
        }

@app.get('/api/protected')
def protected_route(request: Request):
    # Используем стандартную проверку
    user_id = security.get_authenticated_user(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return {"message": f"Hello user {user_id}", "user_id": user_id}

@app.get('/api/me')
def get_current_user(request: Request):
    user_id = security.get_authenticated_user(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return {"user_id": user_id, "authenticated": True}

# WebSocket с проверкой токена
@app.websocket('/ws/{user_id}')
async def websocket_endpoint(
    websocket: WebSocket, 
    user_id: int,
    token: str = None,  # Токен можно передавать в query параметрах
    session: Session = Depends(get_session)
):
    # Проверяем токен для WebSocket
    if token:
        try:
            # Проверяем токен
            payload = security.decode_token(token)
            if str(payload.get("sub")) != str(user_id):
                await websocket.close(code=1008, reason="Invalid token")
                return
        except:
            await websocket.close(code=1008, reason="Authentication failed")
            return
    else:
        # Если токен не передан, можно запросить его при подключении
        # или использовать другие методы проверки
        pass
    
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            data = await websocket.receive_json()
            
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
    request: Request,
    session: Session = Depends(get_session)
):
    """Получение истории переписки между двумя пользователями"""
    # Проверяем авторизацию
    current_user = security.get_authenticated_user(request)
    if not current_user or int(current_user) != user_id:
        raise HTTPException(status_code=401, detail="Not authorized")
    
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

@app.post('/api/send_message')
async def send_message(
    data: MessageSchema,
    request: Request,
    session: Session = Depends(get_session)
):
    """Отправка сообщения через HTTP (полезно для отладки)"""
    # Проверяем авторизацию
    user_id = security.get_authenticated_user(request)
    if not user_id or int(user_id) != data.sender_id:
        raise HTTPException(status_code=401, detail="Not authorized")
    
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

# Эндпоинт для логаута
@app.post('/api/logout')
def logout(request: Request):
    # В JWT логаут обычно реализуется на клиенте (удаление токена)
    # Но можно добавить blacklist токенов, если нужно
    return {"message": "Logout successful (clear token on client)"}

# Добавим middleware для обработки OPTIONS запросов
@app.middleware("http")
async def handle_options_requests(request: Request, call_next):
    if request.method == "OPTIONS":
        from fastapi.responses import Response
        return Response(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "http://localhost:3000",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Authorization, Content-Type",
                "Access-Control-Allow-Credentials": "true",
            }
        )
    
    response = await call_next(request)
    
    # Добавляем CORS заголовки ко всем ответам
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)