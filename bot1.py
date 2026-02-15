import telebot
import requests
import os
from yt_dlp import YoutubeDL
from telebot import types
from flask import Flask
from threading import Thread

# --- Render Flask Server ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Online! 🚀"
def run(): app.run(host='0.0.0.0', port=10000)
def keep_alive():
    t = Thread(target=run)
    t.start()

# --- CONFIGURATION ---
API_TOKEN = '8351525966:AAGd_LMfjJVtzCSYjqZZ3WIi0dq82tAmm5E'
ADMIN_ID = 7854988070 
bot = telebot.TeleBot(API_TOKEN)

def main_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("📥 Download Video", "☎️ Support")
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "🚀 **Smart Downloader v4.6**\nDirect Upload Enabled! ✅", reply_markup=main_keyboard())

@bot.message_handler(func=lambda m: m.text == "📥 Download Video")
def ask_for_link(message):
    msg = bot.send_message(message.chat.id, "🔗 **Please send the video link:**")
    bot.register_next_step_handler(msg, process_video)

def process_video(message):
    url = message.text
    chat_id = message.chat.id
    status = bot.send_message(chat_id, "⚡ **Processing & Downloading... Please Wait!**")

    # --- টিকটক ও ইউটিউব সরাসরি ডাউনলোড অপশন ---
    file_name = f"video_{chat_id}.mp4"
    ydl_opts = {
        'quiet': True,
        'format': 'best[ext=mp4]/best',
        'outtmpl': file_name, # ফাইলটি সরাসরি সেভ হবে
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'nocheckcertificate': True
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True) # সরাসরি ডাউনলোড হচ্ছে
            title = info.get('title', 'Video')
            
            bot.delete_message(chat_id, status.message_id)
            bot.send_message(chat_id, f"📤 **Uploading:** {title[:50]}...")
            
            # সরাসরি ফাইল টেলিগ্রামে পাঠানো
            with open(file_name, 'rb') as video:
                bot.send_video(chat_id, video, caption=f"🎬 **{title}**\n\n✅ Done Boss!")
            
            os.remove(file_name) # কাজ শেষ হলে ফাইল ডিলিট
            
    except Exception as e:
        if os.path.exists(file_name): os.remove(file_name)
        bot.edit_message_text(f"❌ **Error!** This video is too large or blocked by YouTube.", chat_id, status.message_id)

# --- SUPPORT SYSTEM ---
@bot.message_handler(func=lambda m: m.text == "☎️ Support")
def support(message):
    msg = bot.send_message(message.chat.id, "✍️ **Write your problem:**", reply_markup=types.ForceReply())
    bot.register_next_step_handler(msg, send_to_admin)

def send_to_admin(message):
    bot.send_message(ADMIN_ID, f"📩 **New Message!**\n👤 From: {message.from_user.first_name}\n💬 Message: {message.text}")
    bot.send_message(message.chat.id, "✅ **Message Sent!**", reply_markup=main_keyboard())

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()

