from pydantic import BaseModel
from typing import Optional

class UserSchema(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    
    class Config:
        from_attributes = True

class MessageCreate(BaseModel):
    sender_id: int
    recipient_id: int
    content: str

class MessageResponse(BaseModel):
    id: int
    sender_id: int
    recipient_id: int
    content: str
    timestamp: Optional[str]
    
    class Config:
        from_attributes = True