import os
import telebot
import requests
import random
import time
from user_agent import generate_user_agent
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("BOT_TOKEN")
GROUP_URL = os.getenv("GROUP_URL", "https://t.me/+am12cx2hyWQ4NWVl")
CHANNEL_URL = os.getenv("CHANNEL_URL", "https://t.me/t_me_ysh")

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

def check_membership(user_id):
    try:
        channel_status = bot.get_chat_member("@t_me_ysh", user_id).status
        group_status = bot.get_chat_member("@am12cx2hyWQ4NWVl", user_id).status
        return channel_status in ["member", "administrator", "creator"] and group_status in ["member", "administrator", "creator"]
    except:
        return False

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id

    if not check_membership(chat_id):
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("Join Group 🔗", url=GROUP_URL),
            InlineKeyboardButton("Join Channel 📢", url=CHANNEL_URL)
        )
        bot.send_message(chat_id, "🚨 **Join our group and channel to use this bot!**", reply_markup=markup, parse_mode="Markdown")
        return

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
        markup.add(
            InlineKeyboardButton("Join Group 🔗", url=GROUP_URL),
            InlineKeyboardButton("Join Channel 📢", url=CHANNEL_URL)
        )
        bot.send_message(chat_id, "🚨 **Join our group and channel to use this bot!**", reply_markup=markup, parse_mode="Markdown")
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

    username = message.text.strip()
    user_data[chat_id]["username"] = username

    lang = user_lang.get(chat_id, "en")

    msg = {
        "en": "📸 **Now send your Instagram post link.**",
        "ml": "📸 **ഇപ്പോൾ നിങ്ങളുടെ Instagram പോസ്റ്റ് ലിങ്ക് അയയ്ക്കുക.**",
        "hi": "📸 **अब अपना इंस्टाग्राम पोस्ट लिंक भेजें।**"
    }

    bot.send_message(chat_id, msg[lang], parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.chat.id in user_data and "post" not in user_data[message.chat.id])
def save_post_link(message):
    chat_id = message.chat.id

    post_link = message.text.strip()
    user_data[chat_id]["post"] = post_link

    lang = user_lang.get(chat_id, "en")

    bot.send_message(chat_id, "⏳ **Processing... Please wait.**", parse_mode="Markdown")

    boost_instagram(chat_id)

def boost_instagram(chat_id):
    lang = user_lang.get(chat_id, "en")
    user = user_data[chat_id]["username"]
    post = user_data[chat_id]["post"]
    ua = generate_user_agent()
    email = f"{random.randint(1000, 9999)}{int(time.time())}@gmail.com"

    headers = {'user-agent': ua}
    json_data = {'link': post, 'instagram_username': user, 'email': email}

    res = requests.post('https://api.likesjet.com/freeboost/7', headers=headers, json=json_data)
    api_response = res.json()

    if 'Success!' in api_response:
        response = {
            "en": "✅ **Boost successful!**",
            "ml": "✅ **ബൂസ്റ്റ് വിജയകരം!**",
            "hi": "✅ **बूस्ट सफल हुआ!**"
        }
    elif "already used" in api_response.get("message", ""):
        response = {
            "en": "❌ **You have reached the free boost limit. Try later.**",
            "ml": "❌ **നിങ്ങൾ ഫ്രീ ബൂസ്റ്റ് ലിമിറ്റ് എത്തിച്ചേർന്നു. പിന്നീടു ശ്രമിക്കുക.**",
            "hi": "❌ **आपने मुफ्त बूस्ट की सीमा पार कर ली है। बाद में कोशिश करें।**"
        }
    else:
        response = api_response.get("message", "Unknown error")

    bot.send_message(chat_id, response[lang], parse_mode="Markdown")
    user_data.pop(chat_id, None)

bot.polling()
