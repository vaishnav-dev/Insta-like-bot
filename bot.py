import telebot
import requests
import random
import os
import time
from user_agent import generate_user_agent
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("BOT_TOKEN")  # Use environment variable for security
bot = telebot.TeleBot(TOKEN)

user_lang = {}  # Store user language preferences
user_data = {}  # Temporary storage for username & post link

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("English 🇬🇧", callback_data="lang_en"),
        InlineKeyboardButton("Malayalam 🇮🇳", callback_data="lang_ml")
    )
    bot.send_message(chat_id, "Choose language / ഭാഷ തിരഞ്ഞെടുക്കുക:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def set_language(call):
    chat_id = call.message.chat.id
    lang = call.data.split("_")[1]
    user_lang[chat_id] = lang

    welcome_msg = (
        "🎉 Welcome to **Instagram Like Booster Bot!**\n\n"
        "✅ **Increase likes on your Instagram post for free!**\n"
        "👉 **If you need help, contact @yshzap.**"
        if lang == "en" else
        "🎉 **ഇൻസ്റ്റാഗ്രാം ലൈക്ക് ബൂസ്റ്റർ ബോട്ടിലേക്ക് സ്വാഗതം!**\n\n"
        "✅ **നിങ്ങളുടെ Instagram പോസ്റ്റിൽ ലൈക്കുകൾ വർദ്ധിപ്പിക്കുക!**\n"
        "👉 **സഹായം ആവശ്യമാണോ? @yshzap എന്നെ സമീപിക്കുക.**"
    )
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Increase Post Likes 👍", callback_data="increase_likes"))
    
    bot.send_message(chat_id, welcome_msg, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "increase_likes")
def ask_username(call):
    chat_id = call.message.chat.id
    lang = user_lang.get(chat_id, "en")

    msg = (
        "✏️ **Send your Instagram username** (without `@`).\n\n"
        "⚠️ **Your account must be public!**"
        if lang == "en" else
        "✏️ **നിങ്ങളുടെ ഇൻസ്റ്റാഗ്രാം യൂസർനെയിം അയയ്ക്കുക** (`@` വേണ്ട).\n\n"
        "⚠️ **നിങ്ങളുടെ അക്കൗണ്ട് പബ്ലിക് ആകണം!**"
    )
    
    user_data[chat_id] = {}  # Reset user data
    bot.send_message(chat_id, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.chat.id in user_data and "username" not in user_data[message.chat.id])
def save_username(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "en")

    username = message.text.strip()
    
    if "@" in username or " " in username:
        error_msg = (
            "❌ **Invalid username!** Send only your username, without `@` or spaces."
            if lang == "en" else
            "❌ **അസാധുവായ യൂസർനെയിം!** `@` അല്ലെങ്കിൽ സ്പെയ്സ് ഇല്ലാതെ നിങ്ങളുടെ യൂസർനെയിം അയയ്ക്കുക."
        )
        bot.send_message(chat_id, error_msg, parse_mode="Markdown")
        return

    user_data[chat_id]["username"] = username  # Save username

    msg = (
        "📸 **Now send your Instagram post link.**"
        if lang == "en" else
        "📸 **ഇപ്പോൾ നിങ്ങളുടെ Instagram പോസ്റ്റ് ലിങ്ക് അയയ്ക്കുക.**"
    )
    bot.send_message(chat_id, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.chat.id in user_data and "post" not in user_data[message.chat.id])
def save_post_link(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "en")

    post_link = message.text.strip()
    
    if "instagram.com/p/" not in post_link:
        error_msg = (
            "❌ **Invalid post link!** Send a correct Instagram post link."
            if lang == "en" else
            "❌ **അസാധുവായ പോസ്റ്റ് ലിങ്ക്!** ശരിയായ Instagram പോസ്റ്റ് ലിങ്ക് അയയ്ക്കുക."
        )
        bot.send_message(chat_id, error_msg, parse_mode="Markdown")
        return

    user_data[chat_id]["post"] = post_link  # Save post link

    msg = (
        "⏳ **Processing... Please wait.**"
        if lang == "en" else
        "⏳ **പ്രോസസ്സ് ചെയ്യുന്നു... കാത്തിരിക്കുക.**"
    )
    bot.send_message(chat_id, msg, parse_mode="Markdown")

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
        response = (
            "✅ **Boost successful!**"
            if lang == "en" else
            "✅ **റോഷ് വിജയകരമായി!**"
        )
    elif "already used" in api_response.get("message", ""):
        response = (
            "❌ **You have reached the free boost limit. Try later.**"
            if lang == "en" else
            "❌ **നിങ്ങൾ പരമാവധി ഉപയോഗിച്ചു. പിന്നീട് ശ്രമിക്കുക.**"
        )
    else:
        response = f" **Log:** {api_response.get('message', 'Unknown error')}"

    bot.send_message(chat_id, response, parse_mode="Markdown")
    user_data.pop(chat_id, None)  # Clear user data

bot.polling()
