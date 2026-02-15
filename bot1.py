import telebot
from yt_dlp import YoutubeDL
from telebot import types
from flask import Flask
from threading import Thread

# --- Render-কে সচল রাখার জন্য Flask সার্ভার (এটি আপনার দেওয়া কোডের সাথে যুক্ত করা হলো) ---
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
# আপনার দেওয়া নতুন এপিআই টোকেন নিচে বসানো হয়েছে
API_TOKEN = '8351525966:AAGd_LMfjJVtzCSYjqZZ3WIi0dq82tAmm5E'
ADMIN_ID = 7854988070 
bot = telebot.TeleBot(API_TOKEN)


# ডাটা সেভ রাখার জন্য
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
    status = bot.send_message(chat_id, "⚡ **Generating Best Link...**")


    # সব সোশ্যাল মিডিয়া (Insta, FB, YT) সাপোর্ট করার জন্য উন্নত সেটিংস
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'best[ext=mp4]/best',
        'referer': 'https://www.instagram.com/', # ইনস্টাগ্রাম সাপোর্টের জন্য
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
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
                    f"👇 নিচের বাটন থেকে ডাউনলোড করুন:"
                )


                bot.delete_message(chat_id, status.message_id)
                
                if thumbnail:
                    bot.send_photo(chat_id, thumbnail, caption=caption, reply_markup=markup, parse_mode="Markdown")
                else:
                    bot.send_message(chat_id, caption, reply_markup=markup, parse_mode="Markdown")
            else:
                bot.edit_message_text("❌ সরাসরি লিঙ্ক পাওয়া যায়নি।", chat_id, status.message_id)


    except Exception as e:
        bot.edit_message_text("❌ Error: লিঙ্কটি কাজ করছে না বা এটি প্রাইভেট ভিডিও।", chat_id, status.message_id)
        print(f"Error: {e}")


# --- ☎️ SUPPORT / MESSAGE TO ADMIN ---
@bot.message_handler(func=lambda m: m.text == "☎️ Support")
def support(message):
    msg = bot.send_message(message.chat.id, "✍️ **আপনার সমস্যাটি লিখে পাঠান (এটি অ্যাডমিনের কাছে যাবে):**", reply_markup=types.ForceReply())
    bot.register_next_step_handler(msg, send_to_admin)


def send_to_admin(message):
    user_msg = message.text
    user_name = message.from_user.first_name
    user_id = message.from_user.id
    
    # অ্যাডমিনকে মেসেজ পাঠানো
    bot.send_message(ADMIN_ID, f"📩 **New Support Message!**\n\n👤 From: {user_name}\n🆔 ID: `{user_id}`\n\n💬 Message: {user_msg}", parse_mode="Markdown")
    
    # ইউজারকে কনফার্ম করা
    bot.send_message(message.chat.id, "✅ **আপনার মেসেজটি অ্যাডমিনের কাছে পাঠানো হয়েছে!** ধন্যবাদ।", reply_markup=main_keyboard())


if __name__ == "__main__":
    keep_alive() # রেন্ডারের জন্য সার্ভার চালু করা
    print("🚀 Super Fast Bot v4.6 is Online!")
    bot.infinity_polling()
