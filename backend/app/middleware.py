from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import re

# Список публичных маршрутов (доступны без авторизации)
PUBLIC_PATHS = [
    '/api/auth',
    '/api/create_user',
    '/docs',
    '/redoc',
    '/openapi.json',
    '/favicon.ico',
]

# WebSocket соединения также должны обрабатываться отдельно
WEBSOCKET_PATH_PATTERN = re.compile(r'^/ws/\d+$')

class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware для проверки авторизации"""
    
    async def dispatch(self, request: Request, call_next):
        # Получаем путь запроса
        path = request.url.path
        
        # Проверяем, является ли путь публичным
        is_public = (
            path in PUBLIC_PATHS or
            any(path.startswith(p) for p in PUBLIC_PATHS if p.endswith('*')) or
            WEBSOCKET_PATH_PATTERN.match(path)
        )
        
        # Для WebSocket проверяем токен в query параметрах
        if path.startswith('/ws/'):
            return await call_next(request)
        
        # Если путь публичный - пропускаем
        if is_public:
            return await call_next(request)
        
        # Проверяем авторизацию для защищенных маршрутов
        try:
            # Используем вашу существующую функцию проверки
            from .auth import security
            user = security.get_authenticated_user(request)
            
            if not user:
                # Если не авторизован и пытается получить API
                if path.startswith('/api/'):
                    raise HTTPException(status_code=401, detail="Not authenticated")
                
                # Для остальных запросов перенаправляем на логин
                # (предполагаем, что фронтенд на отдельном порту)
                return Response(
                    status_code=403,
                    content="Access denied. Please authenticate first."
                )
            
            # Если пользователь авторизован и пытается зайти на страницу логина
            if path in ['/', '/login', '/register']:
                # Перенаправляем на главную
                return RedirectResponse(url='/main')
            
        except Exception as e:
            if path.startswith('/api/'):
                raise HTTPException(status_code=401, detail=str(e))
            return Response(
                status_code=403,
                content="Authentication failed"
            )
        
        # Пропускаем запрос дальше
        return await call_next(request)