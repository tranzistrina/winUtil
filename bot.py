import os
import telebot
import math
import random

bot = telebot.TeleBot(os.getenv("TELEGRAM_BOT_TOKEN"))

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я бот, который может вычислять синус, косинус, тангенс и котангенс угла. Просто отправь мне сообщение в формате 'градусы минуты операция', где операция: 1 - синус, 2 - косинус, 3 - тангенс, 4 - котангенс.")

# Function to read haikus from the file
def read_haikus_from_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        haikus = [line.strip() for line in file.readlines()]
    return haikus

# File containing haikus
kohu_file = 'kohu.txt'

# List of haikus
haikus = read_haikus_from_file(kohu_file)

@bot.message_handler(commands=['kohu'])
def send_kohu(message):
    # Check if the message is from the specified group
    if message.chat.title == "8б срач":
        return  # Ignore messages from this group
    kohu = random.choice(haikus)
    bot.send_message(message.chat.id, kohu)

@bot.message_handler(func=lambda m: True)
def echo_all(message):
    try:
        degrees, minutes, operation = map(int, message.text.split())
        angle_in_radians = math.radians(degrees + minutes / 60)
        if operation == 1:
            result = math.sin(angle_in_radians)
        elif operation == 2:
            result = math.cos(angle_in_radians)
        elif operation == 3:
            result = math.tan(angle_in_radians)
        elif operation == 4:
            result = 1 / math.tan(angle_in_radians)
        else:
            raise ValueError
        bot.reply_to(message, f"Результат: {result}")
    except ValueError:
        bot.reply_to(message, "Пожалуйста, отправьте сообщение в правильном формате: 'градусы минуты операция'.")

bot.polling()
