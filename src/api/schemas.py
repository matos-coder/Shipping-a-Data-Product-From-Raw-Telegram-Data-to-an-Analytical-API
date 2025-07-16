# src/api/schemas.py
from pydantic import BaseModel
from typing import List

# Schema for a single message search result
class Message(BaseModel):
    message_id: int
    message_text: str
    view_count: int

    class Config:
        orm_mode = True

# Schema for channel activity
class ChannelActivity(BaseModel):
    post_date: str
    message_count: int

    class Config:
        orm_mode = True

# Schema for top detected objects
class TopObject(BaseModel):
    detected_object_name: str
    mention_count: int

    class Config:
        orm_mode = True
