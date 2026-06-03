from pydantic import BaseModel
from datetime import datetime

class CreatePost(BaseModel):
    caption:str | None = None

class CommentPost(BaseModel):
    comment:str | None = None