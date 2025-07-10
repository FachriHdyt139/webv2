import os
import re
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask, request

TOKEN = "8049793340:AAF27_KvcsJvMS2Gqz97Hts3SW_GKevofgE"
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # URL untuk webhook
print("WEBHOOK_URL:", WEBHOOK_URL)  # Pastikan ini tidak None

# Validasi link TikTok
def is_valid_tiktok_url(url):
    pattern = r'(https?://)?(vm\.tiktok\.com/|vt\.tiktok\.com/|www\.tiktok\.com/@[\w\.-]+/video/\d+)'
    return re.search(pattern, url)

# Fungsi /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Selamat datang di Bot Downloader TikTok!\n\n"
        "Kirim link video TikTok dan aku akan mengunduhnya untukmu.\n"
        "MEMEK:\n/"
    )

# Fungsi /help
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 *Panduan:*\n"
        "1. Copy link video dari TikTok\n"
        "2. Kirim ke bot ini\n"
        "3. Bot akan kirim videonya (tanpa watermark)\n\n"
        "Bot ini juga akan otomatis menghapus file setelah terkirim agar hemat storage.",
        parse_mode='Markdown'
    )

# Fungsi utama download TikTok
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if not is_valid_tiktok_url(url):
        await update.message.reply_text("❌ Link TikTok tidak valid. Kirim link video TikTok yang benar.")
        return

    await update.message.reply_text("⏳ Mengunduh video...")

    try:
        # Panggil API TikWM (tidak butuh API Key)
        api_url = f"https://tikwm.com/api/?url={url}"
        res = requests.get(api_url)
        data = res.json()

        if not data.get("data") or not data["data"].get("play"):
            await update.message.reply_text("⚠️ Gagal mendapatkan video.")
            return

        video_url = data["data"]["play"]
        title = data["data"].get("title", "Video TikTok")

        # Download ke file lokal
        video_file = "tiktok_video.mp4"
        with open(video_file, "wb") as f:
            f.write(requests.get(video_url).content)

        # Kirim video ke user
        await update.message.reply_video(
            video=open(video_file, "rb"),
            caption=f"✅ {title}"
        )

        # Hapus file setelah terkirim
        os.remove(video_file)
        print(f"✔️ File {video_file} berhasil dihapus dari penyimpanan.")

    except Exception as e:
        await update.message.reply_text(f"❌ Terjadi kesalahan: {e}")

# Flask Setup
app = Flask(__name__)

@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = Update.de_json(json_str, bot)  # Panggil Update dengan benar
    application.update_queue.put(update)    # Letakkan update ke queue
    return 'OK'

if __name__ == '__main__':
    # Setup bot dengan ApplicationBuilder
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Set webhook URL to Render server
    if WEBHOOK_URL:
        application.bot.set_webhook(WEBHOOK_URL + '/' + TOKEN)
        print(f"Webhook set to: {WEBHOOK_URL + '/' + TOKEN}")
    else:
        print("❌ WEBHOOK_URL belum diatur!")

    # Jalankan Flask app
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
