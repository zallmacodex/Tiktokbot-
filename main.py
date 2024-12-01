import telebot
import requests
import os

# Ganti dengan token bot Anda
BOT_TOKEN = "7994188138:AAHzCkrbNU94wTqqfWUO-An_n7OLuBpaGSQ"

# Inisialisasi bot
bot = telebot.TeleBot(BOT_TOKEN)

# Fungsi untuk memanggil API TikTok
def get_tiktok_data(url):
    api_url = f"https://bs-api-tiktokv2.vercel.app/tiktok?url={url}"
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    return None

# Fungsi untuk mengunduh file dari URL
def download_file(url, filename):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(filename, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        return filename
    return None

# Command /start
@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(message, "Halo! Kirimkan link TikTok yang ingin Anda download (video/audio).")

# Handler untuk menerima pesan berupa link TikTok
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    tiktok_url = message.text.strip()
    bot.reply_to(message, "Sedang memproses link Anda...")
    
    # Ambil data dari API
    data = get_tiktok_data(tiktok_url)
    
    if data and data["status"] == "success":
        video_url = data["data"]["video"]
        audio_url = data["data"]["audio"]
        
        if not video_url and not audio_url:
            bot.reply_to(message, "Maaf, tidak ada video atau audio yang tersedia untuk link ini.")
            return
        
        # Kirim opsi ke pengguna
        markup = telebot.types.InlineKeyboardMarkup()
        if video_url:
            markup.add(
                telebot.types.InlineKeyboardButton(
                    "Download Video", callback_data=f"video|{video_url}"
                )
            )
        if audio_url:
            markup.add(
                telebot.types.InlineKeyboardButton(
                    "Download Audio", callback_data=f"audio|{audio_url}"
                )
            )
        
        bot.send_message(
            message.chat.id,
            "Silakan pilih format yang ingin Anda download:",
            reply_markup=markup
        )
    else:
        bot.reply_to(message, "Maaf, terjadi kesalahan saat memproses link Anda. Pastikan link TikTok valid.")

# Handler untuk callback tombol
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    data = call.data.split("|")
    file_type = data[0]
    file_url = data[1]

    bot.answer_callback_query(call.id, f"Mengunduh {file_type} Anda...")

    # Unduh file dan kirim
    try:
        filename = f"temp_{file_type}.{'mp4' if file_type == 'video' else 'mp3'}"
        downloaded_file = download_file(file_url, filename)
        if downloaded_file:
            with open(downloaded_file, "rb") as file:
                if file_type == "video":
                    bot.send_video(call.message.chat.id, file)
                elif file_type == "audio":
                    bot.send_audio(call.message.chat.id, file)
            os.remove(downloaded_file)  # Hapus file setelah dikirim
        else:
            bot.send_message(call.message.chat.id, "Gagal mengunduh file.")
    except Exception as e:
        bot.send_message(call.message.chat.id, f"Terjadi kesalahan: {e}")

# Jalankan bot
print("Bot sedang berjalan...")
bot.infinity_polling()
