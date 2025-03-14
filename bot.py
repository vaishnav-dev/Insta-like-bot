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
spam_tracker = {}
BAN_TIME = 60

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
    if user_id in spam_tracker:
        spam_tracker[user_id].append(current_time)
        spam_tracker[user_id] = [t for t in spam_tracker[user_id] if current_time - t < 5]
        if len(spam_tracker[user_id]) > 5:
            return True
    else:
        spam_tracker[user_id] = [current_time]
    return False

def ban_user(chat_id):
    bot.send_message(chat_id, "🚨 **You are banned for 1 minute due to spamming.**")
    for i in range(BAN_TIME, 0, -1):
        time.sleep(1)
        try:
            bot.edit_message_text(chat_id=chat_id, message_id=bot.send_message(chat_id, f"⏳ **Ban time left: {i} sec**").message_id, text=f"⏳ **Ban time left: {i} sec**")
        except:
            pass
    del spam_tracker[chat_id]
    bot.send_message(chat_id, "✅ **Ban lifted, you can use the bot again!**")

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    if not check_membership(chat_id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Join Channel 📢", url=CHANNEL_URL))
        markup.add(InlineKeyboardButton("✅ Check Joined", callback_data="check_joined"))
        bot.send_message(chat_id, "🚨 **Join our channel to use this bot!**", reply_markup=markup, parse_mode="Markdown")
        return
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔥 Get Free Likes Now! 👍", callback_data="increase_likes"))
    bot.send_message(chat_id, MESSAGES["welcome"], reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "increase_likes")
def ask_username(call):
    chat_id = call.message.chat.id
    if is_spamming(chat_id):
        ban_user(chat_id)
        return
    bot.send_message(chat_id, "✏️ **Send your Instagram username (without @).**", parse_mode="Markdown")
    user_data[chat_id] = {}

@bot.message_handler(func=lambda message: message.chat.id in user_data and "username" not in user_data[message.chat.id])
def save_username(message):
    chat_id = message.chat.id
    user_data[chat_id]["username"] = message.text.strip()
    bot.send_message(chat_id, "📸 **Now send your Instagram post link.**", parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.chat.id in user_data and "post" not in user_data[message.chat.id])
def save_post_link(message):
    chat_id = message.chat.id
    user_data[chat_id]["post"] = message.text.strip()
    bot.send_chat_action(chat_id, "typing")
    time.sleep(3)
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
