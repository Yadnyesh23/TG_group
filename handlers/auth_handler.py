from pyrogram import Client, filters
from pyrogram.errors import (
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    FloodWait,
    PhoneNumberFlood
)
from pyrogram.types import Message
from database.operations import save_user, get_user
from database.models import User
import os
import re
import asyncio
from dotenv import load_dotenv
import logging
from typing import Optional, Dict, Any

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Dictionary to store login sessions
login_sessions: Dict[int, Dict[str, Any]] = {}

def validate_phone_number(phone: str) -> bool:
    """Validate international phone number format"""
    return bool(re.match(r"^\+\d{8,15}$", phone))

async def cleanup_session(user_id: int):
    """Clean up session resources"""
    if user_id in login_sessions:
        if 'client' in login_sessions[user_id]:
            client = login_sessions[user_id]['client']
            if client.is_connected:
                await client.disconnect()
        del login_sessions[user_id]

def register_handlers(app: Client):
    @app.on_message(filters.command("login"))
    async def login(client: Client, message: Message) -> None:
        """Handle the /login command with multiple delivery methods"""
        if len(message.command) < 2:
            await message.reply(
                "📛 Please provide your phone number in international format.\n"
                "Example: `/login +919876543210`"
            )
            return

        phone = message.command[1]
        if not validate_phone_number(phone):
            await message.reply(
                "❌ Invalid phone format. Must be +CountryCodeNumber\n"
                "Example: `/login +919876543210`"
            )
            return

        try:
            # Cleanup any existing session
            await cleanup_session(message.from_user.id)

            # Initialize client
            user_client = Client(
                f"user_{message.from_user.id}",  # Session name as the first positional argument
                api_id=os.getenv("API_ID"),
                api_hash=os.getenv("API_HASH"),
                phone_number=phone,
                in_memory=True  # Better for temporary sessions
            )

            await user_client.connect()

            # Try normal code delivery first
            try:
                sent_code = await user_client.send_code(phone)
                delivery_method = "Telegram app notification"
            except Exception as e:
                logger.warning(f"Primary code delivery failed, forcing SMS: {e}")
                sent_code = await user_client.send_code(
                    phone_number=phone,
                    force_sms=True
                )
                delivery_method = "SMS"

            # Store session data
            login_sessions[message.from_user.id] = {
                "phone": phone,
                "step": "code",
                "client": user_client,
                "phone_code_hash": sent_code.phone_code_hash,
                "attempts": 0,
                "delivery_method": delivery_method
            }

            response_msg = (
                f"📲 Verification code sent to {phone} via {delivery_method}.\n\n"
                "1. Check your Telegram app notifications\n"
                "2. Or wait for SMS\n\n"
                "Enter the code with: `/verify 12345`\n\n"
                f"⚠️ Didn't receive it? Wait 2 minutes and try `/resend`"
            )

            await message.reply(response_msg)

        except FloodWait as e:
            await message.reply(
                f"⏳ Too many attempts. Please wait {e.value} seconds before trying again."
            )
        except PhoneNumberFlood:
            await message.reply(
                "🚫 This number has been temporarily blocked for too many attempts. "
                "Please try again tomorrow."
            )
        except PhoneNumberInvalid:
            await message.reply("❌ Invalid phone number format. Please check and try again.")
        except Exception as e:
            logger.error(f"Login error for {message.from_user.id}: {str(e)}", exc_info=True)
            await message.reply(
                "❌ Failed to initiate login. Possible reasons:\n"
                "1. Invalid phone number\n"
                "2. Server issues\n"
                "3. Too many attempts\n\n"
                "Please try again later."
            )
            await cleanup_session(message.from_user.id)