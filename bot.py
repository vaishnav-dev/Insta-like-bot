import os
import telebot
import requests
import random
import time
from user_agent import generate_user_agent
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_URL = os.getenv("CHANNEL_URL", "https://t.me/t_me_ysh")

bot = telebot.TeleBot(TOKEN)
user_data = {}
antispam = {}
ban_list = {}

MESSAGES = {
    "welcome": "🎉 Welcome to **Instagram Like Booster Bot!**\n\n✅ **Increase likes on your Instagram post for free!**\n👉 **If you need help, contact @yshzap.**"
}

def check_membership(user_id):
    try:
        channel_status = bot.get_chat_member("@t_me_ysh", user_id).status
        return channel_status in ["member", "administrator", "creator"]
    except:
        return False

def is_spamming(user_id):
    current_time = time.time()
    if user_id in ban_list:
        return True, int(60 - (current_time - ban_list[user_id]))
    if user_id in antispam:
        last_message_time = antispam[user_id]
        if current_time - last_message_time < 2:
            ban_list[user_id] = current_time
            return True, 60
    antispam[user_id] = current_time
    return False, 0

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    is_banned, remaining_time = is_spamming(chat_id)
    if is_banned:
        bot.send_message(chat_id, f"⛔ **You are banned for {remaining_time} seconds!**")
        return
    if not check_membership(chat_id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Join Channel 📢", url=CHANNEL_URL))
        markup.add(InlineKeyboardButton("✅ Check Joined", callback_data="check_joined"))
        bot.send_message(chat_id, "🚨 **Join our channel to use this bot!**", reply_markup=markup, parse_mode="Markdown")
        return
    bot.send_message(chat_id, MESSAGES["welcome"], parse_mode="Markdown")
    ask_boost(chat_id)

@bot.callback_query_handler(func=lambda call: call.data == "increase_likes")
def ask_username(call):
    chat_id = call.message.chat.id
    bot.send_message(chat_id, "✏️ **Send your Instagram username (without @).**", parse_mode="Markdown")
    user_data[chat_id] = {}

@bot.message_handler(func=lambda message: message.chat.id in user_data and "username" not in user_data[message.chat.id])
def save_username(message):
    chat_id = message.chat.id
    is_banned, remaining_time = is_spamming(chat_id)
    if is_banned:
        bot.send_message(chat_id, f"⛔ **You are banned for {remaining_time} seconds!**")
        return
    user_data[chat_id]["username"] = message.text.strip()
    bot.send_message(chat_id, "📸 **Now send your Instagram post link.**", parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.chat.id in user_data and "post" not in user_data[message.chat.id])
def save_post_link(message):
    chat_id = message.chat.id
    is_banned, remaining_time = is_spamming(chat_id)
    if is_banned:
        bot.send_message(chat_id, f"⛔ **You are banned for {remaining_time} seconds!**")
        return
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
    try:
        res = requests.post('https://api.likesjet.com/freeboost/7', headers=headers, json=json_data)
        api_response = res.json()
        if 'Success!' in api_response:
            response = "✅ **Boost successful!**"
        elif "already used" in api_response.get("message", ""):
            response = "❌ **You have reached the free boost limit. Try later.**"
        else:
            response = f"❌ **Error:** {api_response.get('message', 'Unknown error')}"
    except Exception as e:
        response = f"❌ **Request failed:** {str(e)}"
    bot.send_message(chat_id, response, parse_mode="Markdown")
    user_data.pop(chat_id, None)

bot.polling()
