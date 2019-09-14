from pydantic import BaseModel
from typing import int, String, List
from datetime import datetime

class Message(BaseModel):
    id: int
    text: String
    room_id: int
    username: String
    created_at: datetime

class Room(BaseModel):
    id: int
    name: String

class User(BaseModel):
    id: int
    username: String