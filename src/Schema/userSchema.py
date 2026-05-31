from pydantic import BaseModel
from datetime import datetime

class CreateUser(BaseModel):
    name:str
    email:str
    mobile:str
    createdAt: datetime
    password:str
    username:str

class LoginUser(BaseModel):
    email:str
    password:str

class UpdateProfile(BaseModel):
    name:str | None = None
    email:str | None = None
    mobile:str | None = None  
    username:str | None = None