from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.auth import createAccount, login
from app.database import get_session, setup_database

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить все origins для разработки
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все методы
    allow_headers=["*"],  # Разрешить все заголовки
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
    
    # http://localhost:8000/api/create_user