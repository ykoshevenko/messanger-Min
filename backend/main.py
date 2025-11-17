from fastapi import FastAPI, HTTPException
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from pydantic import BaseModel
from app.auth import createAccaunt, login
from app.database import get_session

app = FastAPI()

class User(BaseModel):
    username: str
    password: str

@app.post('/api/create_user')
async def add_user(data:User):
    async with get_session() as session:
        try:
            return await createAccaunt(data, session)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
@app.get('/api/auth')
async def authinticated(data:User):
    try:
        return await login(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))