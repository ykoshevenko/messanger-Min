# from fastapi import FastAPI, HTTPException, Depends
# from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
# from pydantic import BaseModel
# from app.auth import createAccaunt, login
# from app.database import get_session, setup_database

# app = FastAPI()

# class User(BaseModel):
#     username: str
#     password: str

# @app.on_event("startup")
# def on_startup():
#     setup_database()
#     print("Database initialized")

# @app.post('/api/create_user')
# async def create_user(data: User, session: AsyncSession = Depends(get_session)):
#     try:
#         await createAccaunt(data, session)
#         raise HTTPException(status_code=201, detail='register complieted')
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    
# @app.post('/api/auth')
# async def authinticated(data: User, session: AsyncSession = Depends(get_session)):
#     try:
#         return await login(data, session)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from app.auth import createAccount, login
from app.database import get_session, setup_database

app = FastAPI()

class User(BaseModel):
    username: str
    password: str

# Инициализация базы данных при запуске приложения
@app.on_event("startup")
def on_startup():
    setup_database()
    print("Database initialized")

@app.post('/api/create_user')
def create_user(data: User, session = Depends(get_session)):  # Убрано async
    try:
        createAccount(data, session)  # Убрано await
        return {"message": "User created successfully", "status": 201}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post('/api/auth')
def authenticated(data: User, session = Depends(get_session)):  # Убрано async
    try:
        return login(data, session)  # Убрано await
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # http://localhost:8000/api/create_user