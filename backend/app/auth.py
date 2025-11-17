from authx import AuthX, AuthXConfig
from pydantic import BaseModel
from .database import get_user_by_username, add_user, get_session

class UserLoginSchame(BaseModel):
    username: str
    password: str

config = AuthXConfig()
config.JWT_SECRET_KEY = "SECRET_KEY"
config.JWT_TOKEN_LOCATION = ["headers"]

security = AuthX(config=config)

async def login(creads: UserLoginSchame):
    async with get_session() as session:
        user = await get_user_by_username(creads.username, session)
        if user and user.password == creads.password :
            token = security.create_access_token(uid=user.id)
            return {"access_token": token}
    return {'status_code': 401}

async def createAccaunt(data:UserLoginSchame):
    async with get_session() as session:
        return await add_user(data, session)