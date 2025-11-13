# from pydantic import BaseModel
# from fastapi import HTTPException

# class UserDTO(BaseModel):
#     id: int
#     login: str
#     password: str

# class Token(BaseModel):
#     access_token:str
#     token_type:str
#     access_token_expires:str

# class UserAuth():
#     def validate_user(self, login: str, password: str):
#         user:UserDTO = user.repository.select_user_by_login(login)

#         if user and user.password.__eq__(password):
#             return user
#         else:
#             return False
        
#     def login_for_access_token(self, login:str, password:str) -> Token:
#         user:UserDTO = self.validate_user(login, password)

#         if not user:
#             raise HTTPException(
#                 status_code=401,
#                 detail="Incorrect username or password",
#                 headers={"WWW-Authenticate": "Bearer"},
#             )
        
#         access_token_expires = timedelta(minutes=15)