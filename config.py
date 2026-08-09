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
