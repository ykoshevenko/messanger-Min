from authx import AuthX, AuthXConfig
from pydantic import BaseModel
from fastapi import HTTPException
from .database import get_user_by_username, add_user

class UserLoginSchema(BaseModel):
    username: str
    password: str

config = AuthXConfig()
config.JWT_SECRET_KEY = "SECRET_KEY"
config.JWT_TOKEN_LOCATION = ["headers"]

security = AuthX(config=config)

def login(creads: UserLoginSchema, session):  
    user = get_user_by_username(creads.username, session)  
    if user and user.password == creads.password:
        token = security.create_access_token(uid=str(user.id))
        return {"access_token": token}
    raise HTTPException(status_code=401, detail='Invalid credentials')

def createAccount(data: UserLoginSchema, session):  
    existing_user = get_user_by_username(data.username, session)  
    if existing_user:
        raise HTTPException(status_code=400, detail='User already exists')
    return add_user(data, session)  