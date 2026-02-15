import telebot
import requests
import os
from yt_dlp import YoutubeDL
from telebot import types


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
    status = bot.send_message(chat_id, "⚡ **Generating Best Link...**")


    # --- স্পেশাল টিকটক হ্যান্ডলার (সরাসরি ডাউনলোড ও আপলোড) ---
    if "tiktok.com" in url or "vt.tiktok" in url:
        try:
            api_url = f"https://tikwm.com/api/?url={url}"
            response = requests.get(api_url).json()


            if response.get('code') == 0:
                video_url = response['data']['play']
                if not video_url.startswith('http'):
                    video_url = "https://tikwm.com" + video_url
                
                file_name = f"tiktok_{chat_id}.mp4"
                
                # ডাউনলোড হচ্ছে...
                r = requests.get(video_url, stream=True)
                with open(file_name, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024*1024):
                        if chunk: f.write(chunk)


                bot.delete_message(chat_id, status.message_id)
                
                # সরাসরি ভিডিও ফাইল পাঠানো
                with open(file_name, 'rb') as video:
                    bot.send_video(chat_id, video, caption="🎬 **Video Ready Boss 😎**\n\n✅ সরাসরি ফাইল আপলোড করা হয়েছে।")
                
                os.remove(file_name) # ফাইল মুছে ফেলা
                return # এখানেই শেষ
        except Exception as e:
            print(f"TikTok Error: {e}")


    # --- সাধারণ মেথড (FB, Insta, YT এর জন্য) ---
    # ইউটিউবের জন্য এখানে কিছু অতিরিক্ত Headers যোগ করা হয়েছে
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
        bot.edit_message_text(f"❌ Error: লিঙ্কটি কাজ করছে না। সার্ভার ইউটিউব ব্লক করে থাকতে পারে।", chat_id, status.message_id)


# --- SUPPORT SYSTEM ---
@bot.message_handler(func=lambda m: m.text == "☎️ Support")
def support(message):
    msg = bot.send_message(message.chat.id, "✍️ **আপনার সমস্যাটি লিখে পাঠান (এটি অ্যাডমিনের কাছে যাবে):**", reply_markup=types.ForceReply())
    bot.register_next_step_handler(msg, send_to_admin)


def send_to_admin(message):
    bot.send_message(ADMIN_ID, f"📩 **New Support Message!**\n\n👤 From: {message.from_user.first_name}\n🆔 ID: `{message.from_user.id}`\n\n💬 Message: {message.text}", parse_mode="Markdown")
    bot.send_message(message.chat.id, "✅ **আপনার মেসেজটি অ্যাডমিনের কাছে পাঠানো হয়েছে!** ধন্যবাদ।", reply_markup=main_keyboard())


print("🚀 Super Fast Bot v4.6 (New Token) is Online!")
bot.infinity_polling()
