# 📨 Telegram "Random Pulse" Messaging Bot

A Python-based Telegram bot that sends a rotating variety of messages to groups at completely random intervals, ranging from 15 minutes to 1 hour between each dispatch.

## ✨ Core Features

- **Jittered Scheduling** – After every sent message, the bot randomly selects the next wait time between 15 minutes (900s) and 1 hour (3600s). This creates an organic, non-spammy presence in groups.
- **Dynamic Message Variety** – Picks a random message from a curated pool on every trigger, ensuring no two consecutive messages are the same (or repeats are rare).
- **Auto-Group Detection** – Instantly detects when added to a new group and begins the randomized schedule without requiring any admin commands.
- **Self-Perpetuating Logic** – The bot schedules its next run immediately after finishing the current send, creating an endless, unpredictable loop.
- **Asynchronous Performance** – Built with python-telegram-bot v20+ and asyncio to handle multiple groups efficiently.

## 🧰 Prerequisites

- Python 3.8+
- A Telegram Bot Token from [@BotFather](https://t.me/BotFather).
- Basic familiarity with virtual environments.

## ⚙️ Installation

### 1. Clone & Setup Environment

```bash
git clone https://github.com/NathenaelTamirat/Channel-follow-telegram-bot-.git
cd Channel-follow-telegram-bot-
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Secure Your Token

Create a `.env` file in the project root:

```text
BOT_TOKEN=your_telegram_bot_token_here
```

## 📝 Configuration (`config.py`)

All customizable parameters live in this file. The magic is in the `MIN_INTERVAL` and `MAX_INTERVAL` variables.

```python
import random

# --- RANDOM INTERVAL BOUNDARIES (in seconds) ---
MIN_INTERVAL = 900   # 15 minutes (minimum wait)
MAX_INTERVAL = 3600  # 60 minutes (maximum wait)

# --- MESSAGE VARIETY POOL ---
# The bot selects one randomly each time it sends.
MESSAGE_POOL = [
    "🌅 Good morning! Hope you're having a great day.",
    "☕ Time for a break! Grab some coffee and stretch.",
    "📊 Quick poll: How is everyone feeling about the current sprint?",
    "🎉 Fun fact: Otters hold hands while sleeping so they don't drift apart.",
    "🤖 Automated insight: Progress over perfection.",
    "💡 Reminder: Don't forget to update your task statuses.",
    "🔥 Keep up the amazing work, everyone!"
]

# --- LOGIC: Fetch a random message ---
def get_random_message():
    """Returns a randomly selected message from the pool."""
    return random.choice(MESSAGE_POOL)
```

## 🚀 Core Architecture (How the Random Interval Works)

Instead of using `run_repeating()` (which requires a fixed interval), this bot uses a recursive self-scheduling pattern:

1. **Bot Starts** → Initializes and listens for groups.
2. **Group Detected** → The bot adds the `chat_id` to an active list and triggers the first immediate send (or first random delay).
3. **Send Message** → The `send_scheduled_message` function is called:
   - It broadcasts the current random message to all stored groups.
   - Crucially, after sending, it calculates `next_wait = random.randint(MIN_INTERVAL, MAX_INTERVAL)`.
   - It then schedules itself to run again using `job_queue.run_once()` with that exact random delay.
4. **Loop** → This creates an infinite, randomized loop that never stops until the bot is killed or removed from all groups.

## 📄 Main Bot File (`bot.py`)

The complete implementation demonstrating this self-scheduling logic. Key handlers:

- `start` – Simple `/start` command for private chats.
- `track_group_join` – Detects when the bot is added to a group, adds it to the active list, sends a welcome message, and kicks off the first random delay.
- `track_group_leave` – Detects when the bot is removed and discards the chat from the active list.
- `send_scheduled_message` – The workhorse: sends a random message to all active groups, then re-schedules itself with a fresh random delay.

## 🏃 Running the Bot

Execute the bot from your terminal:

```bash
python bot.py
```

What happens next:

1. The bot comes online and listens for groups.
2. When you add it to a group, it immediately schedules the first message randomly (e.g., 22 minutes later).
3. After that first message sends, it will wait another random period (e.g., 47 minutes), send again, wait 19 minutes, send again, and so on.

## 📊 Example Flow

| Step | Action | Wait Time (Random) |
|------|--------|--------------------|
| 1    | Bot added to group | Schedules first send in 27 mins |
| 2    | Sends "Good morning!" | Schedules next in 51 mins |
| 3    | Sends "Fun fact about otters" | Schedules next in 18 mins |
| 4    | Sends "Reminder about tasks" | Schedules next in 44 mins |
| ...  | Continues indefinitely | ... |

## 🗄️ Production Recommendations

Since the `active_chats` set is stored in memory, it will be cleared if the bot restarts. For production:

- **Persistent Storage**: Replace the `set()` with a SQLite, PostgreSQL, or Redis database to persist group IDs across restarts.
- **Resuming Jobs**: On bot startup, query your database for existing groups and immediately re-schedule the `send_scheduled_message` function so messages don't stop just because the bot rebooted.
- **Logging**: Python's `logging` module is already wired up for better monitoring.

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Bot sends messages too frequently | Increase the `MIN_INTERVAL` in `config.py` (e.g., to 1800 for 30 mins). |
| Bot sends messages too rarely | Decrease the `MAX_INTERVAL` (e.g., to 2700 for 45 mins). |
| Bot stops sending after a while | Check if the bot was removed from the group. The `try/except` block removes non-existent chat IDs automatically. |
| Initial message takes too long | The first delay uses the same random logic. Modify the `first_delay` variable in `track_group_join` to start faster (e.g., 10 seconds) for testing. |

## 🤝 Contributing

Pull requests are welcome! Please ensure your code follows PEP 8 and includes proper async/await patterns.

## 📜 License

Distributed under the MIT License.
