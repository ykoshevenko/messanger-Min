from fastapi import Request, HTTPException, status
from fastapi.responses import RedirectResponse
from app.auth import security
import re

PUBLIC_ROUTES = [
    "/api/auth",           
    "/api/create_user",    
    "/docs",               
    "/openapi.json",       
    "/favicon.ico",        
    "/ws/",   
]

async def auth_middleware(request: Request, call_next):
    """Middleware для проверки аутентификации с использованием AuthX"""
    
    # Получаем текущий путь
    path = request.url.path
    
    # Проверяем, является ли маршрут публичным
    is_public = any(
        path == route or 
        path.startswith(route) or
        re.match(route.replace("*", ".*"), path) if "*" in route else False
        for route in PUBLIC_ROUTES
    )
    
    # Для WebSocket соединений пропускаем проверку
    if path.startswith("/ws/"):
        response = await call_next(request)
        return response
    
    # Проверяем аутентификацию с помощью AuthX
    is_authenticated = False
    user_id = None
    
    try:
        # AuthX автоматически проверяет токен из куки или заголовка
        current_user = security.get_authenticated_user(request)
        if current_user:
            is_authenticated = True
            user_id = current_user
    except Exception:
        # Если токен невалидный, считаем пользователя неавторизованным
        pass
    
    # Если пользователь на странице аутентификации и уже авторизован - редирект
    if path in ["/api/auth", "/auth", "/login"] and is_authenticated:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    # Если пользователь не авторизован и пытается получить доступ к защищенным страницам
    if not is_authenticated and not is_public:
        # Для API запросов возвращаем 401
        if path.startswith("/api/"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        # Для веб-страниц редирект на страницу аутентификации
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    
    # Если пользователь на главной странице и авторизован - редирект на чат
    if path == "/" and is_authenticated:
        return RedirectResponse(url="/chat", status_code=status.HTTP_302_FOUND)
    
    # Добавляем информацию о пользователе в request.state
    request.state.user_id = user_id
    request.state.is_authenticated = is_authenticated
    
    # Продолжаем обработку запроса
    response = await call_next(request)
    
    return response