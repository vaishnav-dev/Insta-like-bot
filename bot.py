import os
import telebot
import requests
import random
import time
import threading
import logging
from user_agent import generate_user_agent
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Environment variables
TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_URL = os.getenv("CHANNEL_URL", "https://t.me/t_me_ysh")
OWNER_ID = 1776168152  # Owner's Telegram ID

# Initialize bot
bot = telebot.TeleBot(TOKEN)

# User data storage
user_lang = {}
user_data = {}
new_users = set()  # Track new users who use /start

# Language options
LANGUAGES = {
    "en": "English 🇬🇧",
    "ml": "Malayalam 🇮🇳",
    "hi": "Hindi 🇮🇳"
}

# Messages
MESSAGES = {
    "welcome": {
        "en": "🌟 **Welcome to InstaBoost Pro!** 🌟\n\n✨ Get **FREE Instagram likes** in 3 steps:\n1️⃣ Share your username\n2️⃣ Share post link\n3️⃣ Get 100+ likes!\n\n💡 Need help? Contact @yshzap",
        "ml": "🌟 **ഇൻസ്റ്റാബൂസ്റ്റ് പ്രോയ്ക്ക് സ്വാഗതം!** 🌟\n\n✨ 3 ലളിത ഘട്ടങ്ങൾ:\n1️⃣ യൂസർനെയിം അയയ്ക്കുക\n2️⃣ പോസ്റ്റ് ലിങ്ക് അയയ്ക്കുക\n3️⃣ 100+ ലൈക്കുകൾ നേടുക!\n\n💡 സഹായം: @yshzap",
        "hi": "🌟 **InstaBoost Pro में आपका स्वागत है!** 🌟\n\n✨ 3 आसान चरण:\n1️⃣ अपना यूजरनेम भेजें\n2️⃣ पोस्ट लिंक भेजें\n3️⃣ 100+ लाइक पाएं!\n\n💡 सहायता: @yshzap"
    },
    "success": {
        "en": "🎉 **Boost Started!**\n\n✅ Your post will receive likes within 24 hours!\n\n⭐ Enjoying this service? Share us with friends:\n{CHANNEL_URL}",
        "ml": "🎉 **ലൈക്കുകൾ ആരംഭിച്ചു!**\n\n✅ 24 മണിക്കൂറിനുള്ളിൽ ലൈക്കുകൾ ലഭിക്കും!\n\n⭐ സേവനം ഇഷ്ടമായോ? സുഹൃത്തുക്കളുമായി പങ്കിടുക:\n{CHANNEL_URL}",
        "hi": "🎉 **लाइक्स शुरू हो गए!**\n\n✅ 24 घंटे के भीतर लाइक्स प्राप्त होंगे!\n\n⭐ सेवा पसंद आई? मित्रों के साथ साझा करें:\n{CHANNEL_URL}"
    }
}

# Helper function to check channel membership
def check_membership(user_id):
    try:
        channel_status = bot.get_chat_member("@t_me_ysh", user_id).status
        return channel_status in ["member", "administrator", "creator"]
    except Exception as e:
        logger.error(f"Error checking membership: {e}")
        return False

# Start command handler
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    username = message.from_user.username if message.from_user.username else "No username"

    logger.info(f"New /start command from user: @{username} (ID: {chat_id})")

    if chat_id not in new_users:
        new_users.add(chat_id)
        owner_msg = f"🆕 **New User Started the Bot!**\n\n👤 Username: @{username}\n🆔 ID: `{chat_id}`"
        bot.send_message(OWNER_ID, owner_msg, parse_mode="Markdown")

    if not check_membership(chat_id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("✨ Join Channel (Required)", url=CHANNEL_URL))
        markup.add(InlineKeyboardButton("✅ I've Joined", callback_data="check_joined"))
        bot.send_message(chat_id, "🔒 **Access Required**\n\nJoin our channel to unlock FREE Instagram likes! 👇", reply_markup=markup, parse_mode="Markdown")
        return

    show_language_selection(chat_id)

# Check if user joined after clicking "I've Joined"
@bot.callback_query_handler(func=lambda call: call.data == "check_joined")
def check_if_joined(call):
    chat_id = call.message.chat.id
    if check_membership(chat_id):
        bot.send_message(chat_id, "✅ **You have joined!**\n\nNow you can access the bot.", parse_mode="Markdown")
        show_language_selection(chat_id)
    else:
        bot.send_message(chat_id, "❌ **You're not in the channel!**\n\nPlease join first and then click 'I've Joined'.", parse_mode="Markdown")

# Language selection handler
def show_language_selection(chat_id):
    markup = InlineKeyboardMarkup()
    for lang_code, lang_name in LANGUAGES.items():
        markup.add(InlineKeyboardButton(lang_name, callback_data=f"lang_{lang_code}"))
    bot.send_message(chat_id, "Choose language / ഭാഷ തിരഞ്ഞെടുക്കുക / भाषा चुनें:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def set_language(call):
    chat_id = call.message.chat.id
    lang = call.data.split("_")[1]
    user_lang[chat_id] = lang

    bot.send_message(chat_id, f"✅ **Language set to {LANGUAGES[lang]}**", parse_mode="Markdown")

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Increase Post Likes 👍", callback_data="increase_likes"))

    bot.send_message(chat_id, MESSAGES["welcome"][lang], reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "increase_likes")
def ask_username(call):
    chat_id = call.message.chat.id
    lang = user_lang.get(chat_id, "en")

    user_data[chat_id] = {}

    bot.send_message(chat_id, "📝 **Step 1/2**\n\nSend your Instagram username (example: `insta_user123`):", parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.chat.id in user_data and "username" not in user_data[message.chat.id])
def save_username(message):
    chat_id = message.chat.id
    user_data[chat_id]["username"] = message.text.strip()

    bot.send_message(chat_id, "🔗 **Step 2/2**\n\nSend your Instagram post link (example: `https://www.instagram.com/p/ABC123/`)", parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.chat.id in user_data and "post" not in user_data[message.chat.id])
def save_post_link(message):
    chat_id = message.chat.id
    user_data[chat_id]["post"] = message.text.strip()

    msg = bot.send_message(chat_id, "⏳ **Processing Request...**\n\nWe're generating your likes! Please wait ⏱️", parse_mode="Markdown")

    threading.Thread(target=boost_instagram, args=(chat_id, msg.message_id)).start()

def boost_instagram(chat_id, msg_id):
    user = user_data[chat_id]["username"]
    post = user_data[chat_id]["post"]
    ua = generate_user_agent()
    email = f"{random.randint(1000, 9999)}{int(time.time())}@gmail.com"

    headers = {'user-agent': ua}
    json_data = {'link': post, 'instagram_username': user, 'email': email}

    res = requests.post('https://api.likesjet.com/freeboost/7', headers=headers, json=json_data)
    api_response = res.json()

    lang = user_lang.get(chat_id, "en")

    if 'Success!' in api_response:
        success_msg = MESSAGES["success"][lang].format(CHANNEL_URL=CHANNEL_URL)
        bot.send_message(chat_id, success_msg, parse_mode="Markdown")
    else:
        failure_reason = api_response.get("error", "Unknown error occurred.")
        bot.send_message(chat_id, f"⚠️ **Boost Failed!**\n\n❌ Reason: {failure_reason}", parse_mode="Markdown")

    user_data.pop(chat_id, None)

bot.polling()
