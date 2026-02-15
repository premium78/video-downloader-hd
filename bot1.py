import telebot
import requests
import os
from yt_dlp import YoutubeDL
from telebot import types
from flask import Flask
from threading import Thread

# --- Render-কে সচল রাখার জন্য Flask সার্ভার (যাতে Port Error না আসে) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is Running! 🚀"

def run():
    # Render সাধারণত ১০০০০ পোর্ট ব্যবহার করে
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- ⚙️ CONFIGURATION ---
# আপনার দেওয়া নতুন এপিআই টোকেন এখানে বসানো হয়েছে
API_TOKEN = '8351525966:AAGd_LMfjJVtzCSYjqZZ3WIi0dq82tAmm5E'
ADMIN_ID = 7854988070 
bot = telebot.TeleBot(API_TOKEN)

def main_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("📥 Download Video", "☎️ Support")
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "🚀 **Smart Downloader v5.0**\nYouTube & TikTok Fixed with Flask! ✅", reply_markup=main_keyboard())

@bot.message_handler(func=lambda m: m.text == "📥 Download Video")
def ask_for_link(message):
    msg = bot.send_message(message.chat.id, "🔗 **Please send the video link:**")
    bot.register_next_step_handler(msg, process_video)

def process_video(message):
    url = message.text
    chat_id = message.chat.id
    status = bot.send_message(chat_id, "⚡ **Generating Best Link...**")

    # --- স্পেশাল টিকটক হ্যান্ডলার ---
    if "tiktok.com" in url or "vt.tiktok" in url:
        try:
            api_url = f"https://tikwm.com/api/?url={url}"
            response = requests.get(api_url).json()
            if response.get('code') == 0:
                video_url = response['data']['play']
                file_name = f"tiktok_{chat_id}.mp4"
                r = requests.get(video_url, stream=True)
                with open(file_name, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024*1024):
                        if chunk: f.write(chunk)
                bot.delete_message(chat_id, status.message_id)
                with open(file_name, 'rb') as video:
                    bot.send_video(chat_id, video, caption="🎬 **Video Ready Boss 😎**")
                os.remove(file_name)
                return
        except Exception as e:
            print(f"TikTok Error: {e}")

    # --- সাধারণ মেথড (YT/FB/Insta - কুকিজ সহ) ---
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'best[ext=mp4]/best',
        'cookiefile': 'cookies.txt',  # আপনার আপলোড করা ফাইলটি ব্যবহার করবে
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'nocheckcertificate': True
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Video')
            download_url = info.get('url')

            if download_url:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("📥 Download Now", url=download_url))
                bot.delete_message(chat_id, status.message_id)
                bot.send_message(chat_id, f"🎬 **Video Ready Boss 😎**\n\n📌 **Title:** {title[:60]}...\n\n👇 নিচের বাটন থেকে ডাউনলোড করুন:", reply_markup=markup, parse_mode="Markdown")
            else:
                bot.edit_message_text("❌ সরাসরি লিঙ্ক পাওয়া যায়নি।", chat_id, status.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Error: ইউটিউব বা সার্ভার ব্লক করেছে। কুকিজ ফাইলটি চেক করুন।", chat_id, status.message_id)

# --- SUPPORT SYSTEM ---
@bot.message_handler(func=lambda m: m.text == "☎️ Support")
def support(message):
    msg = bot.send_message(message.chat.id, "✍️ সমস্যাটি লিখে পাঠান:", reply_markup=types.ForceReply())
    bot.register_next_step_handler(msg, send_to_admin)

def send_to_admin(message):
    bot.send_message(ADMIN_ID, f"📩 **New Message!**\n\n👤 From: {message.from_user.first_name}\n💬 Message: {message.text}")
    bot.send_message(message.chat.id, "✅ মেসেজ পাঠানো হয়েছে!", reply_markup=main_keyboard())

if __name__ == "__main__":
    keep_alive() # Flask সার্ভার চালু করা
    print("🚀 Super Fast Bot v5.0 is Online!")
    bot.infinity_polling()
