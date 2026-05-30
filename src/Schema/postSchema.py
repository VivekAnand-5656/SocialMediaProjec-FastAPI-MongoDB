from pydantic import BaseModel
from datetime import datetime

class CreatePost(BaseModel):
    caption:str 
