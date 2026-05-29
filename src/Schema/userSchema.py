from pydantic import BaseModel
from datetime import datetime

class CreateUser(BaseModel):
    name:str
    email:str
    mobile:str
    createdAt: datetime
    password:str

class LoginUser(BaseModel):
    email:str
    password:str

