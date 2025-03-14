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
        bot.send_message(chat_id, "Language set to English. Send your Instagram username and post link in this format:\n\n`username|post_link`", parse_mode="Markdown")
    else:
        bot.send_message(chat_id, "ഭാഷ മലയാളം ആയി സെറ്റ് ചെയ്തു. നിങ്ങളുടെ ഇൻസ്റ്റാഗ്രാം യൂസർനെയിമും പോസ്റ്റ് ലിങ്കും ഈ ഫോർമാറ്റിൽ അയയ്ക്കുക:\n\n`username|post_link`", parse_mode="Markdown")

@bot.message_handler(func=lambda message: '|' in message.text)
def boost_instagram(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "en")  # Default to English if no language is set

    try:
        user, post = message.text.split('|')
        ua = str(generate_user_agent())
        random_id = random.randint(100, 999)

        # Generate a unique email to avoid blocks
        email = f"{int(time.time())}@gmail.com"

        headers = {
            'authority': 'api.likesjet.com',
            'accept': 'application/json, text/plain, */*',
            'content-type': 'application/json',
            'origin': 'https://likesjet.com',
            'referer': 'https://likesjet.com/',
            'user-agent': ua
        }

        json_data = {
            'link': post.strip(),
            'instagram_username': user.strip(),
            'email': email,
        }

        res = requests.post('https://api.likesjet.com/freeboost/7', headers=headers, json=json_data)
        api_response = res.json()  # Get full API response

        print("API Response:", api_response)  # Print API response for debugging

        if 'Success!' in api_response:
            response = "✅ Boost successful!" if lang == "en" else "✅ റോഷ് വിജയകരമായി!"
        else:
            response = f"❌ API Error: {api_response}"  # Show full error message

        bot.reply_to(message, response)

    except Exception as e:
        error_msg = f"Error: {str(e)}" if lang == "en" else f"പിശക്: {str(e)}"
        bot.reply_to(message, error_msg)

bot.polling()
