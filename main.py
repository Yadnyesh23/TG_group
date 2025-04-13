import os
from pyrogram import Client, filters
from pyrogram.types import Message
from dotenv import load_dotenv
from handlers import (
    auth_handler,
    group_handler,
    message_handler,
    help_handler
)

load_dotenv()

app = Client(
    "bot",
    api_id=os.getenv("API_ID"),
    api_hash=os.getenv("API_HASH"),
    bot_token=os.getenv("BOT_TOKEN")
)

# Register handlers
auth_handler.register_handlers(app)
group_handler.register_handlers(app)
message_handler.register_handlers(app)
help_handler.register_handlers(app)

@app.on_message(filters.command("start"))
async def start(client: Client, message: Message):
    await message.reply("🤖 Welcome to the Telegram Bot! Type /help to see available commands.")

if __name__ == "__main__":
    print("Bot started...")
    app.run()