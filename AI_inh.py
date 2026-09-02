import os
import logging
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
MAX_MESSAGE_LENGTH = 4096

def get_model_response(prompt):
    try:
        process = subprocess.Popen(['ollama', 'run', 'deepseek-r1:8b'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='replace')
        stdout, stderr = process.communicate(input=prompt + "\n")
        logging.info(f"Вывод модели: {stdout}")
        logging.error(f"Ошибки модели: {stderr}")
        return stdout.strip() if stdout else "Модель не вернула ответ."
    except Exception as e:
        logging.error(f"Ошибка при взаимодействии с моделью: {e}")
        return "Произошла ошибка при обработке запроса."

def split_message(message, max_length=MAX_MESSAGE_LENGTH):
    return [message[i:i + max_length] for i in range(0, len(message), max_length)]

async def start(update: Update, context):
    await update.message.reply_text('Привет! Я бот, который общается с моделью INH. Напиши мне что-нибудь!')

async def handle_message(update: Update, context):
    user_message = update.message.text
    logging.info(f"Получено сообщение: {user_message}")
    model_response = get_model_response(user_message)
    for part in split_message(model_response):
        await update.message.reply_text(part)

def main():
    application = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == '__main__':
    main()