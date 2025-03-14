import os
import telebot
import requests
import random
import time
from user_agent import generate_user_agent
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "YOUR_BOT_TOKEN"
GROUP_ID = -1001234567890  # Replace with actual Group ID (from @userinfobot)
CHANNEL_USERNAME = "@t_me_ysh"  # Use channel username (for private channels)
GROUP_URL = "https://t.me/+am12cx2hyWQ4NWVl"
CHANNEL_URL = "https://t.me/t_me_ysh"

bot = telebot.TeleBot(TOKEN)

user_lang = {}  # Stores user's selected language
user_data = {}  # Temporary storage for username & post link

LANGUAGES = {
    "en": "English 🇬🇧",
    "ml": "Malayalam 🇮🇳",
    "hi": "Hindi 🇮🇳",
    "ta": "Tamil 🇮🇳",
    "te": "Telugu 🇮🇳",
    "kn": "Kannada 🇮🇳"
}

MESSAGES = {
    "welcome": {
        "en": "🎉 Welcome to **Instagram Like Booster Bot!**\n\n✅ **Increase likes on your Instagram post for free!**",
        "ml": "🎉 **ഇൻസ്റ്റാഗ്രാം ലൈക്ക് ബൂസ്റ്റർ ബോട്ടിലേക്ക് സ്വാഗതം!**\n\n✅ **നിങ്ങളുടെ Instagram പോസ്റ്റിൽ ലൈക്കുകൾ വർദ്ധിപ്പിക്കുക!**",
        "hi": "🎉 **इंस्टाग्राम लाइक बूस्टर बॉट में आपका स्वागत है!**\n\n✅ **अपने इंस्टाग्राम पोस्ट पर लाइक बढ़ाएं!**"
    }
}

def check_membership(user_id):
    try:
        channel_status = bot.get_chat_member(CHANNEL_USERNAME, user_id).status
        group_status = bot.get_chat_member(GROUP_ID, user_id).status
        return channel_status in ["member", "administrator", "creator"] and group_status in ["member", "administrator", "creator"]
    except:
        return False

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id

    if not check_membership(chat_id):
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("Join Group 🔗", url=GROUP_URL),
            InlineKeyboardButton("Join Channel 📢", url=CHANNEL_URL)
        )
        markup.add(InlineKeyboardButton("✅ Check Joined", callback_data="check_joined"))
        bot.send_message(chat_id, "🚨 **Join our group and channel to use this bot!**", reply_markup=markup, parse_mode="Markdown")
        return

    markup = InlineKeyboardMarkup()
    for lang_code, lang_name in LANGUAGES.items():
        markup.add(InlineKeyboardButton(lang_name, callback_data=f"lang_{lang_code}"))
    
    bot.send_message(chat_id, "Choose language / ഭാഷ തിരഞ്ഞെടുക്കുക:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check_joined")
def check_joined(call):
    chat_id = call.message.chat.id

    if check_membership(chat_id):
        bot.send_message(chat_id, "✅ **You have joined!** Now you can use the bot.")
    else:
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("Join Group 🔗", url=GROUP_URL),
            InlineKeyboardButton("Join Channel 📢", url=CHANNEL_URL)
        )
        markup.add(InlineKeyboardButton("✅ Check Again", callback_data="check_joined"))
        bot.send_message(chat_id, "❌ **You haven't joined yet!** Please join and then click 'Check Again'.", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def set_language(call):
    chat_id = call.message.chat.id
    lang = call.data.split("_")[1]
    user_lang[chat_id] = lang

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Increase Post Likes 👍", callback_data="increase_likes"))
    
    bot.send_message(chat_id, MESSAGES["welcome"].get(lang, MESSAGES["welcome"]["en"]), reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "increase_likes")
def ask_username(call):
    chat_id = call.message.chat.id

    if not check_membership(chat_id):
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("Join Group 🔗", url=GROUP_URL),
            InlineKeyboardButton("Join Channel 📢", url=CHANNEL_URL)
        )
        markup.add(InlineKeyboardButton("✅ Check Joined", callback_data="check_joined"))
        bot.send_message(chat_id, "🚨 **Join our group and channel to use this bot!**", reply_markup=markup, parse_mode="Markdown")
        return

    bot.send_message(chat_id, "✏️ **Send your Instagram username** (without `@`).", parse_mode="Markdown")
    user_data[chat_id] = {}  # Reset user data

@bot.message_handler(func=lambda message: message.chat.id in user_data and "username" not in user_data[message.chat.id])
def save_username(message):
    chat_id = message.chat.id

    username = message.text.strip()
    user_data[chat_id]["username"] = username  # Save username

    bot.send_message(chat_id, "📸 **Now send your Instagram post link.**", parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.chat.id in user_data and "post" not in user_data[message.chat.id])
def save_post_link(message):
    chat_id = message.chat.id

    post_link = message.text.strip()
    user_data[chat_id]["post"] = post_link  # Save post link

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
        response = "✅ **Boost successful!**"
    elif "already used" in api_response.get("message", ""):
        response = "❌ **You have reached the free boost limit. Try later.**"
    else:
        response = f"{api_response.get('message', 'Unknown error')}"

    bot.send_message(chat_id, response, parse_mode="Markdown")
    user_data.pop(chat_id, None)

bot.polling()
