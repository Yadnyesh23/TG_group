from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class User(BaseModel):
    user_id: int
    phone: str
    session_string: str
    created_at: datetime = datetime.now()
    last_active: datetime = datetime.now()
    is_active: bool = True

class UserMessage(BaseModel):
    user_id: int
    message_text: str
    created_at: datetime = datetime.now()

class UserGroups(BaseModel):
    user_id: int
    group_ids: List[int]
    updated_at: datetime = datetime.now()