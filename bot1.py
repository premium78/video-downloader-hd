import telebot
import requests
import os
from yt_dlp import YoutubeDL
from telebot import types
from flask import Flask
from threading import Thread

# --- Render-কে সচল রাখার জন্য Flask সার্ভার ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is Running! 🚀"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- ⚙️ CONFIGURATION ---
# আপনার দেওয়া নতুন এপিআই টোকেন নিচে বসানো হয়েছে
API_TOKEN = '8351525966:AAGd_LMfjJVtzCSYjqZZ3WIi0dq82tAmm5E'
ADMIN_ID = 7854988070 
bot = telebot.TeleBot(API_TOKEN)

video_cache = {}

def main_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("📥 Download Video", "☎️ Support")
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "🚀 **Smart Downloader v4.6**\nAll Social Media Supported! ✅", reply_markup=main_keyboard())

@bot.message_handler(func=lambda m: m.text == "📥 Download Video")
def ask_for_link(message):
    msg = bot.send_message(message.chat.id, "🔗 **Please send the video link:**")
    bot.register_next_step_handler(msg, process_video)

def process_video(message):
    url = message.text
    chat_id = message.chat.id
    status = bot.send_message(chat_id, "⚡ **Generating Best Link... Please Wait!**")

    # --- স্পেশাল টিকটক হ্যান্ডলার (TikWM API ব্যবহার করে ফিক্স করা হয়েছে) ---
    if "tiktok.com" in url or "vt.tiktok" in url:
        try:
            api_url = f"https://tikwm.com/api/?url={url}"
            response = requests.get(api_url).json()

            if response.get('code') == 0:
                video_url = response['data']['play']
                if not video_url.startswith('http'):
                    video_url = "https://tikwm.com" + video_url
                
                file_name = f"tiktok_{chat_id}.mp4"
                
                r = requests.get(video_url, stream=True)
                with open(file_name, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024*1024):
                        if chunk: f.write(chunk)

                bot.delete_message(chat_id, status.message_id)
                
                with open(file_name, 'rb') as video:
                    bot.send_video(chat_id, video, caption="🎬 **Video Ready Boss 😎**\n\n✅ Directly Uploaded!")
                
                os.remove(file_name) 
                return 
        except Exception as e:
            bot.edit_message_text("❌ **TikTok Downloader failed! Try again later.**", chat_id, status.message_id)
            return

    # --- সাধারণ মেথড (FB, Insta, YT এর জন্য) ---
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'best[ext=mp4]/best',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'referer': 'https://www.google.com/',
        'nocheckcertificate': True
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Video')
            duration = info.get('duration_string', 'Unknown')
            thumbnail = info.get('thumbnail')
            download_url = info.get('url')

            if download_url:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("📥 Download Now", url=download_url))

                caption = (
                    f"🎬 **Video Ready Boss 😎**\n\n"
                    f"📌 **Title:** {title[:60]}...\n"
                    f"⏱ **Duration:** {duration}\n"
                    f"✅ **Quality:** Best (With Sound)\n\n"
                    f"👇 **Click the button below to download:**"
                )

                bot.delete_message(chat_id, status.message_id)
                
                if thumbnail:
                    bot.send_photo(chat_id, thumbnail, caption=caption, reply_markup=markup, parse_mode="Markdown")
                else:
                    bot.send_message(chat_id, caption, reply_markup=markup, parse_mode="Markdown")
            else:
                bot.edit_message_text("❌ **Sorry! Download link not found.**", chat_id, status.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ **Error: YouTube blocked or invalid link!**", chat_id, status.message_id)

# --- SUPPORT SYSTEM ---
@bot.message_handler(func=lambda m: m.text == "☎️ Support")
def support(message):
    msg = bot.send_message(message.chat.id, "✍️ **Please write your problem (Admin will see this):**", reply_markup=types.ForceReply())
    bot.register_next_step_handler(msg, send_to_admin)

def send_to_admin(message):
    bot.send_message(ADMIN_ID, f"📩 **New Support Message!**\n\n👤 From: {message.from_user.first_name}\n🆔 ID: `{message.from_user.id}`\n\n💬 Message: {message.text}", parse_mode="Markdown")
    bot.send_message(message.chat.id, "✅ **Success! Your message has been sent to Admin.**", reply_markup=main_keyboard())

if __name__ == "__main__":
    keep_alive() # Render-এর জন্য সার্ভার চালু করা
    print("🚀 Super Fast Bot is Online!")
    bot.infinity_polling()
