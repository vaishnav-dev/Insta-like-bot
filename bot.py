import telebot
import requests
import random
import os
import time
from user_agent import generate_user_agent
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("BOT_TOKEN")  # Use environment variable for security
bot = telebot.TeleBot(TOKEN)

# Dictionary to store user language preferences
user_lang = {}

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("English 🇬🇧", callback_data="lang_en"),
        InlineKeyboardButton("Malayalam 🇮🇳", callback_data="lang_ml")
    )
    bot.send_message(chat_id, "Please select your language:\nദയവായി നിങ്ങളുടെ ഭാഷ തിരഞ്ഞെടുക്കുക:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def set_language(call):
    chat_id = call.message.chat.id
    lang = call.data.split("_")[1]
    user_lang[chat_id] = lang  # Save user language preference

    if lang == "en":
        bot.send_message(chat_id, "✅ Language set to English.\n\nSend your Instagram username and post URL in this format:\n\n`username`\n`post_link`", parse_mode="Markdown")
    else:
        bot.send_message(chat_id, "✅ ഭാഷ മലയാളം ആയി സെറ്റ് ചെയ്തു.\n\nനിങ്ങളുടെ ഇൻസ്റ്റാഗ്രാം യൂസർനെയിം, പോസ്റ്റ് URL ഈ ഫോർമാറ്റിൽ അയയ്ക്കുക:\n\n`username`\n`post_link`", parse_mode="Markdown")

@bot.message_handler(func=lambda message: "\n" in message.text)
def boost_instagram(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "en")  # Default to English if no language is set

    try:
        data = message.text.split("\n")
        if len(data) < 2:
            bot.reply_to(message, "❌ Invalid format! Please send:\n\n`username`\n`post_link`", parse_mode="Markdown")
            return

        user, post = data[0].strip(), data[1].strip()
        ua = str(generate_user_agent())

        # Generate a new random email to avoid blocks
        email = f"{random.randint(1000, 9999)}{int(time.time())}@gmail.com"

        headers = {
            'authority': 'api.likesjet.com',
            'accept': 'application/json, text/plain, */*',
            'content-type': 'application/json',
            'origin': 'https://likesjet.com',
            'referer': 'https://likesjet.com/',
            'user-agent': ua
        }

        json_data = {
            'link': post,
            'instagram_username': user,
            'email': email,
        }

        res = requests.post('https://api.likesjet.com/freeboost/7', headers=headers, json=json_data)
        api_response = res.json()

        print("API Response:", api_response)  # Debugging

        if 'Success!' in api_response:
            response = "✅ Boost successful!" if lang == "en" else "✅ റോഷ് വിജയകരമായി!"
        elif "You have already used our free boost service many times" in api_response.get("message", ""):
            response = "❌ You have reached the free boost limit. Try again later." if lang == "en" else "❌ നിങ്ങൾ സൗജന്യ ബൂസ്റ്റ് പരിധി എത്തിച്ചിരിക്കുന്നു. പിന്നീട് വീണ്ടും ശ്രമിക്കുക."
        else:
            response = f"❌ API Error: {api_response}"  # Show full error message

        bot.reply_to(message, response)

    except Exception as e:
        error_msg = f"Error: {str(e)}" if lang == "en" else f"പിശക്: {str(e)}"
        bot.reply_to(message, error_msg)

bot.polling()
