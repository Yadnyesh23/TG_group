from pyrogram import Client, filters
from pyrogram.types import Message
from database.operations import get_user, get_user_groups, get_user_message  # Ensure these are correctly imported
from typing import Optional


def register_handlers(app: Client):
    @app.on_message(filters.command("help"))
    async def help_command(client: Client, message: Message) -> None:
        """
        Handle the /help command to display available bot commands.
        """
        help_text = """
🤖 Bot Commands:

🔐 Authentication:
/login [phone] - Start login process (e.g., /login +919876543210)
/verify [code] - Verify login with Telegram code
/logout - Log out from your account

👥 Group Management:
/joingroups - Join all groups that bot owner is in
/mygroups - List all groups you've joined

✉️ Messaging:
/setmessage [text] - Set message to broadcast
/preview - Preview your message
/broadcast - Send message to all your groups

🆘 Help:
/help - Show this help message
/status - Show your current status
"""
        await message.reply(help_text)

    @app.on_message(filters.command("status"))
    async def status_command(client: Client, message: Message) -> None:
        """
        Handle the /status command to display the user's current status.
        """
        try:
            user = await get_user(message.from_user.id)
            if user and user.is_active:
                groups = await get_user_groups(message.from_user.id)
                group_count = len(groups.group_ids) if groups else 0
                message_text = await get_user_message(message.from_user.id)

                status_text = f"""
✅ Logged in as: {user.phone}
📋 Groups joined: {group_count}
💬 Message set: {"Yes" if message_text else "No"}
"""
                await message.reply(status_text)
            else:
                await message.reply("❌ You are not logged in. Use /login to start.")
        except Exception as e:
            await message.reply(f"❌ Error retrieving status: {str(e)}")