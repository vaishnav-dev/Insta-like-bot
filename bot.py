import telebot
import requests
import random
import os
import time
from user_agent import generate_user_agent
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("BOT_TOKEN")  # Use environment variable for security
bot = telebot.TeleBot(TOKEN)

# Store user language preferences
user_lang = {}

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

    msg = "Send Instagram username and post link in one message, like this:\n\n`username https://instagram.com/p/your_post`" \
        if lang == "en" else "ഒരു മെസ്സേജിൽ ഇൻസ്റ്റാഗ്രാം യൂസർനെയിമും പോസ്റ്റ് ലിങ്കും അയയ്ക്കുക:\n\n`username https://instagram.com/p/your_post`"
    
    bot.send_message(chat_id, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda message: " " in message.text)
def boost_instagram(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "en")

    try:
        parts = message.text.split(" ", 1)
        if len(parts) != 2:
            bot.reply_to(message, "❌ Invalid format! Send: `username https://instagram.com/p/your_post`", parse_mode="Markdown")
            return

        user, post = parts[0].strip(), parts[1].strip()
        ua = generate_user_agent()
        email = f"{random.randint(1000, 9999)}{int(time.time())}@gmail.com"

        headers = {'user-agent': ua}
        json_data = {'link': post, 'instagram_username': user, 'email': email}

        res = requests.post('https://api.likesjet.com/freeboost/7', headers=headers, json=json_data)
        api_response = res.json()

        if 'Success!' in api_response:
            response = "✅ Boost successful!" if lang == "en" else "✅ റോഷ് വിജയകരമായി!"
        elif "already used" in api_response.get("message", ""):
            response = "❌ You have reached the free boost limit. Try later." if lang == "en" else "❌ നിങ്ങൾ പരമാവധി ഉപയോഗിച്ചു. പിന്നീട് ശ്രമിക്കുക."
        else:
            response = f"❌ API Error: {api_response.get('message', 'Unknown error')}"
        
        bot.reply_to(message, response)

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

bot.polling()
