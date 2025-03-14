import os
import telebot
import requests
import random
import time
from gtts import gTTS
from user_agent import generate_user_agent
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from io import BytesIO

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_URL = os.getenv("CHANNEL_URL", "https://t.me/t_me_ysh")
OWNER_ID = 1776168152
WELCOME_IMAGE_URL = "https://cdn.ironman.my.id/i/apdzmh.jpg"

bot = telebot.TeleBot(TOKEN)

user_lang = {}
user_data = {}

LANGUAGES = {
    "en": {"flag": "🇬🇧", "name": "English"},
    "ml": {"flag": "🇮🇳", "name": "Malayalam"},
    "hi": {"flag": "🇮🇳", "name": "Hindi"}
}

def generate_tts(text, lang_code):
    tts = gTTS(text=text, lang=lang_code[:2], slow=False)
    audio_bytes = BytesIO()
    tts.write_to_fp(audio_bytes)
    audio_bytes.seek(0)
    return audio_bytes

def send_welcome(chat_id, lang_code):
    welcome_text = (
        "🌟 *Welcome to Instagram Like Booster!* 🌟\n\n"
        "🚀 Get your posts trending with FREE likes!\n"
        "📌 Features:\n"
        "✅ Instant like delivery\n"
        "✅ 24/7 Support\n"
        "✅ Multi-language support\n\n"
        "👉 Need help? Contact @yshzap"
    )
    
    # Send welcome image
    bot.send_photo(chat_id, WELCOME_IMAGE_URL, 
                  caption=welcome_text,
                  parse_mode="Markdown")
    
    # Send TTS welcome
    audio = generate_tts(welcome_text.replace('*', ''), lang_code)
    bot.send_voice(chat_id, audio, title="Welcome to Like Booster")

def check_membership(user_id):
    try:
        channel_status = bot.get_chat_member("@t_me_ysh", user_id).status
        return channel_status in ["member", "administrator", "creator"]
    except:
        return False

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    
    # Notify owner about new user
    telegram_user = f"@{message.from_user.username}" if message.from_user.username else "No username"
    owner_msg = (
        f"🆕 *New User Alert!*\n\n"
        f"👤 Username: {telegram_user}\n"
        f"🆔 ID: `{message.chat.id}`\n"
        f"🌐 Language: {user_lang.get(message.chat.id, 'Not set')}"
    )
    bot.send_message(OWNER_ID, owner_msg, parse_mode="Markdown")

    if not check_membership(chat_id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🌟 Join Channel First", url=CHANNEL_URL))
        markup.add(InlineKeyboardButton("✅ I've Joined", callback_data="check_joined"))
        bot.send_message(
            chat_id,
            "📢 *Join our community to unlock the like booster!*",
            reply_markup=markup,
            parse_mode="Markdown"
        )
        return

    show_language_selection(chat_id)

def show_language_selection(chat_id):
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton(
            f"{LANGUAGES[code]['flag']} {LANGUAGES[code]['name']}", 
            callback_data=f"lang_{code}"
        ) for code in LANGUAGES
    ]
    markup.add(*buttons)
    
    bot.send_message(
        chat_id,
        "🌍 *Choose your preferred language:*",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def set_language(call):
    chat_id = call.message.chat.id
    lang = call.data.split("_")[1]
    user_lang[chat_id] = lang
    
    send_welcome(chat_id, lang)
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🚀 Start Boosting Now", callback_data="increase_likes"))
    bot.send_message(
        chat_id,
        "💎 *Ready to boost your Instagram presence?*",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data == "increase_likes")
def ask_username(call):
    chat_id = call.message.chat.id
    if not check_membership(chat_id):
        send_channel_prompt(chat_id)
        return

    lang = user_lang.get(chat_id, "en")
    prompt_text = {
        "en": "📝 *Send your Instagram username* (without @)\n\n🔓 _Make sure your account is public!_",
        "ml": "📝 *Instagram username അയക്കുക* (@ ഇല്ലാതെ)\n\n🔓 _അക്കൗണ്ട് പബ്ലിക് ആയിരിക്കണം!_",
        "hi": "📝 *अपना इंस्टाग्राम यूजरनेम भेजें* (@ के बिना)\n\n🔓 _खाता सार्वजनिक होना चाहिए!_"
    }
    
    user_data[chat_id] = {}
    bot.send_message(chat_id, prompt_text[lang], parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.chat.id in user_data and "username" not in user_data[message.chat.id])
def save_username(message):
    chat_id = message.chat.id
    user_data[chat_id]["username"] = message.text.strip()
    bot.send_message(
        chat_id,
        "🔗 *Now send your Instagram post link*\n\n"
        "📎 Example: https://www.instagram.com/p/Cxample123/",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda message: message.chat.id in user_data and "post" not in user_data[message.chat.id])
def save_post_link(message):
    chat_id = message.chat.id
    user_data[chat_id]["post"] = message.text.strip()
    
    # Animated processing message
    processing_msg = bot.send_message(chat_id, "⏳ *Processing your request...*", parse_mode="Markdown")
    for emoji in ["🔍", "📡", "🚀"]:
        time.sleep(1)
        bot.edit_message_text(
            f"{emoji} *Processing your request...*",
            chat_id=chat_id,
            message_id=processing_msg.message_id,
            parse_mode="Markdown"
        )
    
    boost_instagram(chat_id)

def boost_instagram(chat_id):
    lang = user_lang.get(chat_id, "en")
    user = user_data[chat_id]["username"]
    post = user_data[chat_id]["post"]
    
    try:
        headers = {'user-agent': generate_user_agent()}
        json_data = {
            'link': post,
            'instagram_username': user,
            'email': f"{random.randint(1000,9999)}{int(time.time())}@gmail.com"
        }
        
        response = requests.post('https://api.likesjet.com/freeboost/7', headers=headers, json=json_data)
        api_data = response.json()

        # Get message directly from API response
        result_text = api_data.get("message", "Operation completed")
        
        # Send TTS response
        audio = generate_tts(result_text, lang)
        bot.send_voice(chat_id, audio)
        bot.send_message(
            chat_id,
            f"📢 *Status Update:*\n\n{result_text}",
            parse_mode="Markdown"
        )

    except Exception as e:
        error_text = f"⚠️ *Oops! Something went wrong:*\n\n{str(e)}"
        bot.send_message(
            chat_id,
            error_text + "\n\n📩 Please contact @yshzap for assistance",
            parse_mode="Markdown"
        )
    finally:
        user_data.pop(chat_id, None)

bot.polling()
