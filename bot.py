import os
import logging
import random
from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ChatMemberStatus
from telegram.ext import (
    Application,
    ChatMemberHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
import config

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Store all active group chat IDs (use a database/Redis for production)
active_chats = set()


async def debug_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Temporary debug handler: dumps every received update."""
    print("\n========== UPDATE RECEIVED ==========")
    print(update)
    print("=====================================\n")


async def start(update, context):
    """Simple /start command for private chats."""
    await update.message.reply_text(
        "👋 Add me to a group and I will send random messages "
        "at random intervals between 15 minutes and 1 hour!"
    )


async def track_chat_member(update, context):
    """
    Detects when the bot itself is added to, or removed from, a group.
    Adds/removes the group from the active list and triggers the first
    message cycle on join.
    """
    chat_member = update.chat_member or update.my_chat_member
    # Only react when the change is about the bot itself
    if chat_member.new_chat_member.user.id != context.bot.id:
        return

    new_status = chat_member.new_chat_member.status
    chat_id = chat_member.chat.id

    if new_status == ChatMemberStatus.MEMBER:
        is_new = chat_id not in active_chats
        active_chats.add(chat_id)

        welcome_msg = (
            "✅ Bot activated! I will now send random messages to this group. "
            f"Next message will arrive in {random.randint(config.MIN_INTERVAL, config.MAX_INTERVAL) // 60} minutes."
        )
        await context.bot.send_message(chat_id=chat_id, text=welcome_msg)
        logger.info("Activated bot in chat %s", chat_id)

        # Schedule the FIRST message with a random initial delay so the loop starts.
        # If a loop is already running, don't spawn a second concurrent one.
        if is_new and not any(j.name == "pulse" for j in context.job_queue.jobs()):
            first_delay = random.randint(config.MIN_INTERVAL, config.MAX_INTERVAL)
            context.job_queue.run_once(
                send_scheduled_message,
                when=first_delay,
                chat_id=chat_id,
                name="pulse",
            )
    elif new_status in (ChatMemberStatus.LEFT, ChatMemberStatus.BANNED):
        active_chats.discard(chat_id)
        logger.info("Removed from chat %s", chat_id)


async def send_scheduled_message(context):
    """
    The workhorse function.
    1. Sends a varied message to all active groups.
    2. Schedules ITSELF to run again after a NEW random delay.
    """
    if not active_chats:
        logger.info("No active chats; pausing the loop.")
        return  # No groups to send to, stop the cycle until a new group joins.

    # 1. Pick a fresh random message
    message_text = config.get_random_message()

    # 2. Send to all active groups
    for chat_id in list(active_chats):
        try:
            await context.bot.send_message(chat_id=chat_id, text=message_text)
        except Exception as e:
            # If bot was removed from this group, remove it from our list
            logger.warning("Failed to send to %s: %s", chat_id, e)
            active_chats.discard(chat_id)

    # 3. --- THE RANDOM RESCHEDULING LOGIC ---
    # Calculate a NEW random delay between 15min and 1hr
    next_delay = random.randint(config.MIN_INTERVAL, config.MAX_INTERVAL)

    # Schedule this EXACT same function to run again after that delay.
    # We pass chat_id=None because we loop over all chats inside the function.
    context.job_queue.run_once(send_scheduled_message, when=next_delay, name="pulse")

    # (Optional) Log the next send time for debugging
    logger.info("Message sent. Next message scheduled in %d minutes.", next_delay // 60)


def build_application():
    app = Application.builder().token(TOKEN).build()

    # Handlers
    app.add_handler(MessageHandler(filters.ALL, debug_update))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        ChatMemberHandler(track_chat_member, ChatMemberHandler.MY_CHAT_MEMBER)
    )
    return app


def main():
    app = build_application()

    # Start polling
    logger.info("Bot is running...")
    app.run_polling(
        allowed_updates=[
            "message",
            "chat_member",
            "my_chat_member",
        ]
    )


if __name__ == "__main__":
    main()
