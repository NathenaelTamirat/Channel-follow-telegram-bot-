import random

# --- RANDOM INTERVAL BOUNDARIES (in seconds) ---
MIN_INTERVAL = 900   # 15 minutes (minimum wait)
MAX_INTERVAL = 3600  # 60 minutes (maximum wait)

# --- MESSAGE VARIETY POOL ---
# The bot selects one randomly each time it sends.
CHANNEL_LINK = "https://t.me/nathenaeltamirat"

MESSAGE_POOL = [
    f"ኑ ተቀላቀሉ! 🚀 ምስጢር እንነግራችኋለን... ወደ ቻናሉ ሲገቡ ብቻ! {CHANNEL_LINK}",
    f"🕵️ 99% የሚያውቁት የሚመስል ነገር እንዳለ ይሰማዎት ነበር? ወደ ውስጥ ገብተው ያረጋግጡ! {CHANNEL_LINK}",
    f"🔥 ይህን ማየት የለብዎትም ነበር። ግን አሁን እያዩት ነው... {CHANNEL_LINK}",
    f"😱 ሰዎች ስለዚህ ነገር ያለማቋረጥ ያወራሉ። እርስዎ ብቻ ናፍቀው ይሆን? {CHANNEL_LINK}",
    f"⚡ አንድ ቁልፍ የሚያውቁት ከሆነ የእለታችሁን ሁሉ ሊቀይር ይችላል... {CHANNEL_LINK}",
    f"🤫 ያውቁት? እዚህ ውስጥ ከባህር በታች የተቀበረ ሀብት አለ። ቻናላችንን ይቀላቀሉ። {CHANNEL_LINK}",
    f"🚨 ማንቂያ: ይህ መረጃ ለጥቂቶች ብቻ የታሰበ ነው። ኑ ተቀላቀሉ! {CHANNEL_LINK}",
    f"🍿 ቀዝቃዛ ምግብዎን ያዙ። ይህ ማንበብ ይፈልጋሉ! {CHANNEL_LINK}",
]

# --- LOGIC: Fetch a random message ---
def get_random_message():
    """Returns a randomly selected message from the pool."""
    return random.choice(MESSAGE_POOL)
