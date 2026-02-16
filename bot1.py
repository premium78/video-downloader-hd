import telebot
import requests
import os
from yt_dlp import YoutubeDL
from telebot import types
from flask import Flask
from threading import Thread

# --- Flask Server (UptimeRobot এর জন্য) ---
app = Flask('')

@app.route('/')
def home():
    return "I am Alive! 🚀"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- ⚙️ CONFIGURATION ---
API_TOKEN = '8351525966:AAGd_LMfjJVtzCSYjqZZ3WIi0dq82tAmm5E'
ADMIN_ID = 7854988070 
bot = telebot.TeleBot(API_TOKEN)

# --- Keyboard ---
def main_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("📥 Download Video", "☎️ Support")
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "🚀 **Smart Downloader v4.6**\nAlways Active Mode Enabled! ✅", reply_markup=main_keyboard())

@bot.message_handler(func=lambda m: m.text == "📥 Download Video")
def ask_for_link(message):
    msg = bot.send_message(message.chat.id, "🔗 **Please send the video link:**")
    bot.register_next_step_handler(msg, process_video)

def process_video(message):
    url = message.text
    chat_id = message.chat.id
    status = bot.send_message(chat_id, "⚡ **Generating Best Link...**")

    # টিকটক হ্যান্ডলার
    if "tiktok.com" in url or "vt.tiktok" in url:
        try:
            api_url = f"https://tikwm.com/api/?url={url}"
            response = requests.get(api_url).json()
            if response.get('code') == 0:
                video_url = response['data']['play']
                bot.delete_message(chat_id, status.message_id)
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("📥 Download TikTok", url=video_url))
                bot.send_message(chat_id, "🎬 **TikTok Ready!**", reply_markup=markup)
                return
        except: pass

    # ইউটিউব ও অন্যান্য
    ydl_opts = {'quiet': True, 'format': 'best[ext=mp4]/best', 'nocheckcertificate': True}
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            download_url = info.get('url')
            bot.delete_message(chat_id, status.message_id)
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("📥 Download File", url=download_url))
            bot.send_message(chat_id, f"🎬 **Ready:** {info.get('title')[:50]}...", reply_markup=markup)
    except:
        bot.edit_message_text("❌ Error: লিঙ্কটি কাজ করছে না।", chat_id, status.message_id)

# --- বটের মেইন লুপ ---
if __name__ == "__main__":
    keep_alive() # সার্ভার এক্টিভ রাখা
    print("🚀 Bot is starting...")
    bot.infinity_polling()
