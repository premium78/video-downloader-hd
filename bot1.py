import telebot
import requests
from yt_dlp import YoutubeDL
from telebot import types
from flask import Flask
from threading import Thread

# --- Flask Server ---
app = Flask('')
@app.route('/')
def home(): return "I am Alive! 🚀"

def run(): app.run(host='0.0.0.0', port=10000)
def keep_alive(): Thread(target=run).start()

# --- CONFIGURATION ---
API_TOKEN = '8351525966:AAGd_LMfjJVtzCSYjqZZ3WIi0dq82tAmm5E'
bot = telebot.TeleBot(API_TOKEN)

def process_video(message):
    url = message.text
    chat_id = message.chat.id
    status = bot.send_message(chat_id, "⚡ **ভিডিওর তথ্য সংগ্রহ করা হচ্ছে...**")

    # ইউটিউব ও ইনস্টাগ্রামের জন্য বিশেষ সেটিংস
    ydl_opts = {
        'quiet': True,
        'format': 'best[ext=mp4]/best',
        'nocheckcertificate': True,
        'no_warnings': True,
        'ignoreerrors': True,
        'cookiefile': 'cookies.txt' # যদি থাকে, না থাকলে সমস্যা নেই
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                raise Exception("তথ্য পাওয়া যায়নি")

            # ডিটেইলস সংগ্রহ করা
            title = info.get('title', 'No Title')
            duration = info.get('duration') # সেকেন্ডে আসবে
            thumbnail = info.get('thumbnail')
            filesize = info.get('filesize_approx') or info.get('filesize')
            
            # সেকেন্ডকে মিনিটে রূপান্তর
            duration_min = f"{duration // 60}:{duration % 60:02d}" if duration else "Unknown"
            
            # সাইজ মেগাবাইটে রূপান্তর
            size_mb = f"{filesize / (1024*1024):.2f} MB" if filesize else "Unknown"

            download_url = info.get('url')
            
            # মেসেজ সাজানো
            caption = (
                f"🎬 **শিরোনাম:** {title}\n"
                f"⏱️ **সময়:** {duration_min}\n"
                f"📦 **সাইজ:** {size_mb}\n\n"
                f"নিচের বাটনে ক্লিক করে ডাউনলোড করুন:"
            )

            bot.delete_message(chat_id, status.message_id)
            
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("📥 Download Now", url=download_url))

            if thumbnail:
                bot.send_photo(chat_id, thumbnail, caption=caption, reply_markup=markup)
            else:
                bot.send_message(chat_id, caption, reply_markup=markup)

    except Exception as e:
        bot.edit_message_text(f"❌ এরর: ভিডিওটি ডাউনলোডযোগ্য নয় বা লিঙ্ক ভুল।", chat_id, status.message_id)

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
