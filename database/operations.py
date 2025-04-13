from motor.motor_asyncio import AsyncIOMotorClient
from .models import User, UserMessage, UserGroups
from dotenv import load_dotenv
import os
import logging
from typing import Optional

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Validate environment variables
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")

if not MONGO_URI or not DATABASE_NAME:
    raise EnvironmentError("MONGO_URI or DATABASE_NAME is not set in the environment variables.")

# Initialize MongoDB client and database
client = AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE_NAME]


async def save_user(user: User) -> None:
    """
    Save or update a user in the database.
    """
    try:
        logger.info(f"Saving user with user_id={user.user_id}")
        await db.users.update_one(
            {"user_id": user.user_id},
            {"$set": user.dict()},
            upsert=True
        )
    except Exception as e:
        logger.error(f"Error saving user with user_id={user.user_id}: {e}")
        raise


async def get_user(user_id: int) -> Optional[User]:
    """
    Retrieve a user from the database by user_id.
    """
    try:
        logger.info(f"Retrieving user with user_id={user_id}")
        user = await db.users.find_one({"user_id": user_id})
        return User(**user) if user else None
    except Exception as e:
        logger.error(f"Error retrieving user with user_id={user_id}: {e}")
        raise


async def save_message(message: UserMessage) -> None:
    """
    Save a user message to the database.
    """
    try:
        logger.info(f"Saving message for user_id={message.user_id}")
        await db.messages.insert_one(message.dict())
    except Exception as e:
        logger.error(f"Error saving message for user_id={message.user_id}: {e}")
        raise


async def get_user_message(user_id: int) -> Optional[UserMessage]:
    """
    Retrieve the latest user message from the database by user_id.
    """
    try:
        logger.info(f"Retrieving latest message for user_id={user_id}")
        message = await db.messages.find_one({"user_id": user_id}, sort=[("created_at", -1)])
        return UserMessage(**message) if message else None
    except Exception as e:
        logger.error(f"Error retrieving message for user_id={user_id}: {e}")
        raise


async def save_user_groups(groups: UserGroups) -> None:
    """
    Save or update user groups in the database.
    """
    try:
        logger.info(f"Saving groups for user_id={groups.user_id}")
        await db.user_groups.update_one(
            {"user_id": groups.user_id},
            {"$set": groups.dict()},
            upsert=True
        )
    except Exception as e:
        logger.error(f"Error saving groups for user_id={groups.user_id}: {e}")
        raise


async def get_user_groups(user_id: int) -> Optional[UserGroups]:
    """
    Retrieve user groups from the database by user_id.
    """
    try:
        logger.info(f"Retrieving groups for user_id={user_id}")
        groups = await db.user_groups.find_one({"user_id": user_id})
        return UserGroups(**groups) if groups else None
    except Exception as e:
        logger.error(f"Error retrieving groups for user_id={user_id}: {e}")
        raise