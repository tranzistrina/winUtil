import os
import telebot

# Указываем токен бота
bot = telebot.TeleBot(os.getenv("TELEGRAM_BOT_TOKEN"))

# Функция для обработки команды /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Я бот для поиска и воспроизведения видео файлов. "
                          "Используй команду /pokazi, чтобы увидеть список видео.")

# Функция для обработки команды /pokazi
@bot.message_handler(commands=['pokazi'])
def pokazi(message):
    video_dir = 'C:\\Users\\lakh\\Desktop\\видосики'
    videos = [f for f in os.listdir(video_dir) if os.path.isfile(os.path.join(video_dir, f)) and f.endswith('.mp4')]
    if videos:
        response = ""
        for i, video in enumerate(videos, start=1):
            video_path = os.path.join(video_dir, video)
            size_mb = os.path.getsize(video_path) / (1024 * 1024)
            response += f"{i}. {video} ({size_mb:.2f} MB)\n"
        bot.reply_to(message, response)
    else:
        bot.reply_to(message, "Видео файлы не найдены.")

# Функция для обработки сообщений с числами
@bot.message_handler(func=lambda message: message.text.isdigit())
def handle_number(message):
    video_dir = 'C:\\Users\\lakh\\Desktop\\видосики'
    videos = [f for f in os.listdir(video_dir) if os.path.isfile(os.path.join(video_dir, f)) and f.endswith('.mp4')]
    try:
        video_number = int(message.text)
        if 1 <= video_number <= len(videos):
            video_path = os.path.join(video_dir, videos[video_number - 1])
            video = open(video_path, 'rb')
            bot.send_video(message.chat.id, video)
        else:
            bot.reply_to(message, "Неверный номер видео.")
    except ValueError:
        pass

# Запускаем бота
bot.polling()
