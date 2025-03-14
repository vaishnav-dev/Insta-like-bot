import os
import telebot
import requests
import random
import time
import threading
from user_agent import generate_user_agent
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_URL = os.getenv("CHANNEL_URL", "https://t.me/t_me_ysh")
OWNER_ID = 1776168152  # Owner's Telegram ID

bot = telebot.TeleBot(TOKEN)

user_lang = {}
user_data = {}

LANGUAGES = {
    "en": "English 🇬🇧",
    "ml": "Malayalam 🇮🇳",
    "hi": "Hindi 🇮🇳"
}

MESSAGES = {
    "welcome": {
        "en": "🎉 Welcome to **Instagram Like Booster Bot!**\n\n✅ **Increase likes on your Instagram post for free!**\n👉 **If you need help, contact @yshzap.**",
        "ml": "🎉 **ഇൻസ്റ്റാഗ്രാം ലൈക്ക് ബൂസ്റ്റർ ബോട്ടിലേക്ക് സ്വാഗതം!**\n\n✅ **നിങ്ങളുടെ Instagram പോസ്റ്റിൽ ലൈക്കുകൾ വർദ്ധിപ്പിക്കുക!**\n👉 **സഹായം ആവശ്യമാണോ? @yshzap എന്നെ സമീപിക്കുക.**",
        "hi": "🎉 **इंस्टाग्राम लाइक बूस्टर बॉट में आपका स्वागत है!**\n\n✅ **अपने इंस्टाग्राम पोस्ट पर लाइक बढ़ाएं!**\n👉 **मदद के लिए @yshzap से संपर्क करें।**"
    }
}

def escape_markdown(text):
    """Escapes special Markdown characters to prevent formatting issues."""
    special_chars = "_*[]()~`>#+-=|{}.!"
    return "".join("\\" + char if char in special_chars else char for char in text)

def check_membership(user_id):
    try:
        channel_status = bot.get_chat_member("@t_me_ysh", user_id).status
        return channel_status in ["member", "administrator", "creator"]
    except:
        return False

def delete_message_after_delay(chat_id, message_id, delay=5):
    time.sleep(delay)
    try:
        bot.delete_message(chat_id, message_id)
    except:
        pass

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id

    threading.Thread(target=delete_message_after_delay, args=(chat_id, message.message_id)).start()

    if not check_membership(chat_id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Join Channel 📢", url=CHANNEL_URL))
        markup.add(InlineKeyboardButton("✅ Check Joined", callback_data="check_joined"))
        bot.send_message(chat_id, "🚨 **Join our channel to use this bot!**", reply_markup=markup, parse_mode="Markdown")
        return

    show_language_selection(chat_id)

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

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Increase Post Likes 👍", callback_data="increase_likes"))
    
    bot.send_message(chat_id, MESSAGES["welcome"][lang], reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "increase_likes")
def ask_username(call):
    chat_id = call.message.chat.id

    if not check_membership(chat_id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Join Channel 📢", url=CHANNEL_URL))
        markup.add(InlineKeyboardButton("✅ Check Joined", callback_data="check_joined"))
        bot.send_message(chat_id, "🚨 **Join our channel to use this bot!**", reply_markup=markup, parse_mode="Markdown")
        return

    lang = user_lang.get(chat_id, "en")

    msg = {
        "en": "✏️ **Send your Instagram username** (without `@`).\n\n⚠️ **Your account must be public!**",
        "ml": "✏️ **നിങ്ങളുടെ Instagram യൂസർനെയിം അയയ്ക്കുക** (`@` ഇല്ലാതെ).\n\n⚠️ **നിങ്ങളുടെ അക്കൗണ്ട് പബ്ലിക്കായിരിക്കണം!**",
        "hi": "✏️ **अपना इंस्टाग्राम यूजरनेम भेजें** (`@` के बिना)।\n\n⚠️ **आपका अकाउंट सार्वजनिक होना चाहिए!**"
    }
    
    user_data[chat_id] = {}
    bot.send_message(chat_id, msg[lang], parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.chat.id in user_data and "username" not in user_data[message.chat.id])
def save_username(message):
    chat_id = message.chat.id
    user_data[chat_id]["username"] = message.text.strip()

    bot.send_message(chat_id, "📸 **Now send your Instagram post link.**", parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.chat.id in user_data and "post" not in user_data[message.chat.id])
def save_post_link(message):
    chat_id = message.chat.id
    user_data[chat_id]["post"] = message.text.strip()

    bot.send_message(chat_id, "⏳ **Processing... Please wait.**", parse_mode="Markdown")
    boost_instagram(chat_id)

def boost_instagram(chat_id):
    user = user_data[chat_id]["username"]
    post = user_data[chat_id]["post"]
    ua = generate_user_agent()
    email = f"{random.randint(1000, 9999)}{int(time.time())}@gmail.com"

    headers = {'user-agent': ua}
    json_data = {'link': post, 'instagram_username': user, 'email': email}

    res = requests.post('https://api.likesjet.com/freeboost/7', headers=headers, json=json_data)
    api_response = res.json()

    if 'Success!' in api_response:
        bot.send_message(chat_id, "✅ **Boost successful!**", parse_mode="Markdown")

        telegram_user = f"@{bot.get_chat(chat_id).username}" if bot.get_chat(chat_id).username else "No username"
        owner_msg = (
            f"📢 **New Order Received!**\n\n"
            f"👤 **Telegram Username:** {escape_markdown(telegram_user)}\n"
            f"🆔 **Telegram ID:** `{chat_id}`\n"
            f"📸 **Instagram Username:** `{escape_markdown(user)}`\n"
            f"🔗 **Post URL:** {escape_markdown(post)}"
        )
        bot.send_message(OWNER_ID, owner_msg, parse_mode="MarkdownV2")
    else:
        error_message = api_response.get("message", "Unknown error occurred.")
        bot.send_message(chat_id, f"❌ **{escape_markdown(error_message)}**", parse_mode="MarkdownV2")

    user_data.pop(chat_id, None)

bot.polling()
