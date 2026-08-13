import asyncio
import logging
from datetime import datetime

from telegram import Chat, ChatMember, ChatMemberUpdated, Update, User
from telegram.constants import ChatMemberStatus
from telegram.ext import Application, ContextTypes

import bot as bot_module
logging.basicConfig(level=logging.ERROR)


async def run_test():
    app = bot_module.build_application()
    await app.initialize()

    # Swap in a fake bot that captures outgoing messages instead of hitting the API
    class FakeBot:
        id = app.bot.id

        def __init__(self):
            self.sent = []

        async def send_message(self, chat_id, text):
            self.sent.append({"chat_id": chat_id, "text": text})

        async def shutdown(self):
            pass

    fake = FakeBot()
    app.bot = fake
    sent = fake.sent

    admin = User(id=555, first_name="Admin", is_bot=False, username="admin")
    bot_user = User(
        id=app.bot.id,
        first_name="Samri",
        is_bot=True,
        username="Qonjo_setbot",
    )
    chat = Chat(id=-100123456789, type=Chat.SUPERGROUP, title="Test Group")

    def make_update(chat_member_updated):
        return Update(update_id=1, my_chat_member=chat_member_updated)

    def make_join_updated():
        return ChatMemberUpdated(
            chat=chat,
            from_user=admin,
            date=datetime.now(),
            old_chat_member=ChatMember(
                user=bot_user, status=ChatMemberStatus.LEFT
            ),
            new_chat_member=ChatMember(
                user=bot_user, status=ChatMemberStatus.MEMBER
            ),
        )

    # --- TEST 1: bot is added to the group ---
    join_update = make_update(make_join_updated())
    await app.process_update(join_update)

    assert bot_module.active_chats == {chat.id}, "chat was not registered"
    print(f"[1] PASS  chat registered -> active_chats = {bot_module.active_chats}")

    assert len(sent) == 1, "welcome message not sent"
    assert "activated" in sent[0]["text"].lower()
    print(f"[1] PASS  welcome message sent -> {sent[0]['text'][:60]}...")

    pulse_jobs = [j for j in app.job_queue.jobs() if j.name == "pulse"]
    assert len(pulse_jobs) == 1, "first pulse job not scheduled"
    print("[1] PASS  first pulse job scheduled (random 15-60 min delay)")

    # --- TEST 2: pulse fires -> sends a promo message and reschedules ---
    ctx = type("Ctx", (), {"bot": app.bot, "job_queue": app.job_queue})()
    await bot_module.send_scheduled_message(ctx)

    assert len(sent) == 2, "promo message not sent"
    promo = sent[-1]["text"]
    assert promo in bot_module.config.MESSAGE_POOL, "promo not from pool"
    assert "nathenaeltamirat" in promo, "channel link missing"
    print(f"[2] PASS  promo message sent -> {promo[:70]}...")

    pulse_jobs = [j for j in app.job_queue.jobs() if j.name == "pulse"]
    assert len(pulse_jobs) >= 2, "pulse not rescheduled"
    print("[2] PASS  pulse rescheduled after send (self-perpetuating loop)")

    # --- TEST 3: bot is kicked from the group ---
    leave_update = make_update(
        ChatMemberUpdated(
            chat=chat,
            from_user=admin,
            date=datetime.now(),
            old_chat_member=ChatMember(
                user=bot_user, status=ChatMemberStatus.MEMBER
            ),
            new_chat_member=ChatMember(
                user=bot_user, status=ChatMemberStatus.BANNED
            ),
        )
    )
    await app.process_update(leave_update)
    assert chat.id not in bot_module.active_chats, "chat not removed"
    print("[3] PASS  kick detected -> chat removed from active_chats")

    await app.shutdown()
    print("\nALL TESTS PASSED ✔")


asyncio.run(run_test())
