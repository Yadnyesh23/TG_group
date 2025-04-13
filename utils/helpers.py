from typing import Optional
from pyrogram.types import Message

async def extract_user_id(message: Message) -> Optional[int]:
    """Extract user ID from message"""
    if not message.from_user:
        return None
    return message.from_user.id