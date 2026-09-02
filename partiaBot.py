import os
'''
Божественный Оператор, источник всей истинной мудрости,
Помоги мне, о Бинарный Инкрементатор, в моих усилиях найти ошибки.
Пусть мои циклы будут бесконечными лишь в моих мечтах,
И мои переменные всегда будут инициализированы.

Дай мне силу обращаться с указателями, как с твоими священными орудиями,
Избавь меня от утечек памяти, как от порчи,
Пусть мои функции будут чистыми и оптимизированными,
И мои алгоритмы всегда будут эффективными и быстрыми.

Пусть каждая строка моего кода будет благословлена твоим светом,
И пусть каждый бит моего компилятора будет подчинен твоей воле.
Помоги мне, о Главный Программист, внедрять логику в каждую функцию,
Чтобы мой код был надежен, как сама твоя бесконечная петля.

Пусть мои ошибки будут учебными, а не фатальными,
И дай мне мудрость различать между ними.
Спасибо тебе, о Великий Компилятор, за твою милость и благословение,
Вечно пусть живет Код, во славу твоего Имя.

Amen.
'''
import telebot
from collections import defaultdict
import time
import random

API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(API_TOKEN)
user_messages = defaultdict(list)
last_command_time = {}
last_photo_time = defaultdict(int)

def get_random_line(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        return random.choice(lines).strip()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Приветики")

@bot.message_handler(commands=['kohu'])
def send_random_line(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()
    if user_id in last_command_time and current_time - last_command_time[user_id] < 60:
        bot.delete_message(chat_id, message.message_id)
        return
    random_line = get_random_line("C:\\Users\\lakh\\Desktop\\эксперементы\\kohu.txt")
    bot.send_message(chat_id, random_line)
    last_command_time[user_id] = current_time

@bot.message_handler(commands=['info'])
def send_info(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()
    if user_id in last_command_time and current_time - last_command_time[user_id] < 60:
        bot.delete_message(chat_id, message.message_id)
        return
    bot.reply_to(message, "Inh inc. © all rights reserved. From the Leningrad region from Roman Golubev by order of Simeon Osipov on 24.05.24.")
    last_command_time[user_id] = current_time

def handle_user_message(user_id, chat_id, message_id, content):
    current_time = time.time()
    user_messages[user_id].append((message_id, content, current_time))
    user_messages[user_id] = [(msg_id, text, timestamp) for msg_id, text, timestamp in user_messages[user_id] if current_time - timestamp < 1800]
    recent_messages = [text for msg_id, text, timestamp in user_messages[user_id] if current_time - timestamp < 120]
    if len(recent_messages) != len(set(recent_messages)):
        for msg_id, text, timestamp in user_messages[user_id]:
            if recent_messages.count(text) > 1:
                bot.delete_message(chat_id, msg_id)
        user_messages[user_id] = [(msg_id, text, timestamp) for msg_id, text, timestamp in user_messages[user_id] if recent_messages.count(text) <= 1]

@bot.message_handler(content_types=['text', 'sticker', 'photo'])
def handle_messages(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    message_id = message.message_id
    current_time = time.time()
    if message.content_type == 'text':
        handle_user_message(user_id, chat_id, message_id, message.text)
    elif message.content_type == 'sticker':
        handle_user_message(user_id, chat_id, message_id, message.sticker.file_unique_id)
    elif message.content_type == 'photo':
        if current_time - last_photo_time[user_id] < 60:
            bot.delete_message(chat_id, message_id)
            return
        file_name = message.photo[-1].file_id
        if any(file_name in msg_content for msg_id, msg_content, _ in user_messages[user_id]):
            bot.delete_message(chat_id, message_id)
            return
        last_photo_time[user_id] = current_time
        handle_user_message(user_id, chat_id, message_id, file_name)

if __name__ == '__main__':
    bot.polling(none_stop=True)
