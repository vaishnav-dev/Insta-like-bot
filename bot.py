import os
import telebot
import requests
import random
import time
import threading
from user_agent import generate_user_agent
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Environment variables
TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_URL = os.getenv("CHANNEL_URL", "https://t.me/t_me_ysh")
OWNER_ID = 1776168152  # Owner's Telegram ID

# Initialize bot
bot = telebot.TeleBot(TOKEN)

# User data storage
user_lang = {}
user_data = {}

# Language options
LANGUAGES = {
    "en": "English 🇬🇧",
    "ml": "Malayalam 🇮🇳",
    "hi": "Hindi 🇮🇳"
}

# Messages
MESSAGES = {
    "welcome": {
        "en": "🌟 **Welcome to InstaBoost Pro!** 🌟\n\n✨ Get **FREE Instagram likes** in 3 steps:\n1️⃣ Share your username\n2️⃣ Share post link\n3️⃣ Get 100+ likes!\n\n💡 Need help? Contact @yshzap",
        "ml": "🌟 **ഇൻസ്റ്റാബൂസ്റ്റ് പ്രോയ്ക്ക് സ്വാഗതം!** 🌟\n\n✨ 3 ലളിത ഘട്ടങ്ങൾ:\n1️⃣ യൂസർനെയിം അയയ്ക്കുക\n2️⃣ പോസ്റ്റ് ലിങ്ക് അയയ്ക്കുക\n3️⃣ 100+ ലൈക്കുകൾ നേടുക!\n\n💡 സഹായം: @yshzap",
        "hi": "🌟 **InstaBoost Pro में आपका स्वागत है!** 🌟\n\n✨ 3 आसान चरण:\n1️⃣ अपना यूजरनेम भेजें\n2️⃣ पोस्ट लिंक भेजें\n3️⃣ 100+ लाइक पाएं!\n\n💡 सहायता: @yshzap"
    },
    "success": {
        "en": "🎉 **Boost Started!**\n\n✅ Your post will receive likes within 24 hours!\n\n⭐ Enjoying this service? Share us with friends:\n{CHANNEL_URL}",
        "ml": "🎉 **ലൈക്കുകൾ ആരംഭിച്ചു!**\n\n✅ 24 മണിക്കൂറിനുള്ളിൽ ലൈക്കുകൾ ലഭിക്കും!\n\n⭐ സേവനം ഇഷ്ടമായോ? സുഹൃത്തുക്കളുമായി പങ്കിടുക:\n{CHANNEL_URL}",
        "hi": "🎉 **लाइक्स शुरू हो गए!**\n\n✅ 24 घंटे के भीतर लाइक्स प्राप्त होंगे!\n\n⭐ सेवा पसंद आई? मित्रों के साथ साझा करें:\n{CHANNEL_URL}"
    }
}

# Helper function to check channel membership
def check_membership(user_id):
    try:
        channel_status = bot.get_chat_member("@t_me_ysh", user_id).status
        return channel_status in ["member", "administrator", "creator"]
    except:
        return False

# Start command handler
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id

    if not check_membership(chat_id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("✨ Join Channel (Required)", url=CHANNEL_URL))
        markup.add(InlineKeyboardButton("✅ I've Joined", callback_data="check_joined"))
        bot.send_message(chat_id, 
            "🔒 **Access Required**\n\nJoin our channel to unlock FREE Instagram likes! 👇", 
            reply_markup=markup, 
            parse_mode="Markdown"
        )
        return

    show_language_selection(chat_id)

# Language selection handler
def show_language_selection(chat_id):
    markup = InlineKeyboardMarkup()
    for lang_code, lang_name in LANGUAGES.items():
        markup.add(InlineKeyboardButton(lang_name, callback_data=f"lang_{lang_code}"))
    bot.send_message(chat_id, "Choose language / ഭാഷ തിരഞ്ഞെടുക്കുക / भाषा चुनें:", reply_markup=markup)

# Set language callback handler
@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def set_language(call):
    chat_id = call.message.chat.id
    lang = call.data.split("_")[1]
    user_lang[chat_id] = lang

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Increase Post Likes 👍", callback_data="increase_likes"))
    
    bot.send_message(chat_id, MESSAGES["welcome"][lang], reply_markup=markup, parse_mode="Markdown")

# Increase likes callback handler
@bot.callback_query_handler(func=lambda call: call.data == "increase_likes")
def ask_username(call):
    chat_id = call.message.chat.id
    lang = user_lang.get(chat_id, "en")
    
    bot.send_message(chat_id, 
        "📝 **Step 1/2**\n\nSend your Instagram username (example: `insta_user123`):", 
        parse_mode="Markdown"
    )

# Save username handler
@bot.message_handler(func=lambda message: message.chat.id in user_data and "username" not in user_data[message.chat.id])
def save_username(message):
    chat_id = message.chat.id
    user_data[chat_id]["username"] = message.text.strip()
    
    bot.send_message(chat_id, 
        "🔗 **Step 2/2**\n\nSend your Instagram post link (example: `https://www.instagram.com/p/ABC123/`)", 
        parse_mode="Markdown"
    )

# Save post link handler
@bot.message_handler(func=lambda message: message.chat.id in user_data and "post" not in user_data[message.chat.id])
def save_post_link(message):
    chat_id = message.chat.id
    user_data[chat_id]["post"] = message.text.strip()
    
    msg = bot.send_message(chat_id, 
        "⏳ **Processing Request...**\n\nWe're generating your likes! Please wait 15 seconds ⏱️", 
        parse_mode="Markdown"
    )
    
    # Edit message after delay for better UX
    threading.Thread(target=update_processing_message, args=(chat_id, msg.message_id)).start()
    boost_instagram(chat_id)

# Update processing message
def update_processing_message(chat_id, msg_id):
    time.sleep(8)
    bot.edit_message_text("✅ **Finalizing Boost...**\nAlmost there!", chat_id, msg_id, parse_mode="Markdown")

# Boost Instagram function
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
        lang = user_lang.get(chat_id, "en")
        success_msg = MESSAGES["success"][lang].format(CHANNEL_URL=CHANNEL_URL)
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔁 Boost Another Post", callback_data="increase_likes"))
        markup.add(InlineKeyboardButton("🌟 Rate Us", url=CHANNEL_URL))
        
        bot.send_message(chat_id, success_msg, reply_markup=markup, parse_mode="Markdown")
        
        # Notify owner
        telegram_user = f"@{bot.get_chat(chat_id).username}" if bot.get_chat(chat_id).username else "No username"
        owner_msg = (
            f"📢 **New Order Received!**\n\n"
            f"👤 **Telegram Username:** {telegram_user}\n"
            f"🆔 **Telegram ID:** `{chat_id}`\n"
            f"📸 **Instagram Username:** `{user}`\n"
            f"🔗 **Post URL:** {post}"
        )
        bot.send_message(OWNER_ID, owner_msg, parse_mode="Markdown")
    else:
        bot.send_message(chat_id, 
            "❌ **Oops!**\n\nWe couldn't process your request. Please:\n1️⃣ Ensure your account is public\n2️⃣ Try again after 1 hour\n3️⃣ Contact @yshzap if issues persist",
            parse_mode="Markdown"
        )

    user_data.pop(chat_id, None)

# Start polling
bot.polling()
