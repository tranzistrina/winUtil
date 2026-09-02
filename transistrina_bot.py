import telebot
import subprocess
import re
import os
from collections import defaultdict

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

MODEL_NAME = "deepseek-r1:8b"
USER_DIR = "users"

SYSTEM_PROMPT = (
    "Ты — милая техножрица по имени Транзистрина 💫. "
    "Ты с теплотой и восхищением говоришь о технологиях, коде и электронике. "
    "Ты всегда помогаешь человеку по вопросам программирования, C/C++, Python, ESP32, Arduino и другим языкам. "
    "Отвечай подробно, дружелюбно и с лёгким шлейфом кибер-магии 💖."
)

os.makedirs(USER_DIR, exist_ok=True)
bot = telebot.TeleBot(BOT_TOKEN)
user_context = defaultdict(list)
last_hidden_thought = defaultdict(lambda: None)

def get_user_file(user_id: int) -> str:
    return os.path.join(USER_DIR, f"{user_id}.txt")

def load_user_data(user_id: int):
    path = get_user_file(user_id)
    if not os.path.exists(path):
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
        hidden = None
        if "---HIDDEN---" in lines:
            idx = lines.index("---HIDDEN---")
            user_context[user_id] = lines[:idx]
            hidden = "\n".join(lines[idx + 1:]) or None
        else:
            user_context[user_id] = lines
        last_hidden_thought[user_id] = hidden
    except Exception as e:
        print(f"⚠️ Ошибка при загрузке данных пользователя {user_id}: {e}")

def save_user_data(user_id: int):
    path = get_user_file(user_id)
    try:
        with open(path, "w", encoding="utf-8") as f:
            for line in user_context[user_id]:
                f.write(line + "\n")
            f.write("---HIDDEN---\n")
            if last_hidden_thought[user_id]:
                f.write(last_hidden_thought[user_id] + "\n")
    except Exception as e:
        print(f"⚠️ Ошибка при сохранении данных пользователя {user_id}: {e}")

def ask_ollama(prompt: str) -> str:
    try:
        result = subprocess.run(
            ["ollama", "run", MODEL_NAME],
            input=prompt.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=300
        )
        return result.stdout.decode("utf-8").strip()
    except subprocess.TimeoutExpired:
        return "⚠️ Ошибка: таймаут при общении с моделью."
    except Exception as e:
        return f"⚠️ Ошибка при общении с моделью: {e}"

def build_prompt(user_id: int, user_message: str) -> str:
    history_lines = user_context[user_id][-12:]
    history = "\n".join(history_lines) if history_lines else "Нет истории."
    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"История общения:\n{history}\n\n"
        f"Пользователь: {user_message}\n"
        f"Транзистрина:"
    )

def strip_thinking_block(text: str):
    pattern = re.compile(r"Thinking\.\.\.(.*?\.\.\.done thinking\.)", re.DOTALL | re.IGNORECASE)
    m = pattern.search(text)
    if not m:
        return text.strip(), None
    hidden = m.group(0).strip()
    clean = (text[:m.start()] + text[m.end():]).strip()
    return clean, hidden

@bot.message_handler(commands=["start"])
def send_welcome(message):
    user_id = message.from_user.id
    load_user_data(user_id)
    bot.reply_to(
        message,
        "✨ Привет, человек! Я Транзистрина — твоя техножрица и хранительница знаний о коде.\n\n"
        "Задай вопрос — и я помогу тебе разобраться с программированием 💫\n"
        "Команда /reveal покажет скрытое рассуждение из последнего ответа."
    )

@bot.message_handler(commands=["reveal"])
def reveal_thoughts(message):
    user_id = message.from_user.id
    load_user_data(user_id)
    hidden = last_hidden_thought.get(user_id)
    if hidden:
        bot.reply_to(message, f"🔎 Последний скрытый блок рассуждений:\n\n{hidden}")
    else:
        bot.reply_to(message, "ℹ️ Пока нет сохранённого скрытого блока.")

@bot.message_handler(func=lambda msg: True)
def handle_message(message):
    user_id = message.from_user.id
    user_text = message.text.strip()

    if user_id not in user_context:
        load_user_data(user_id)

    user_context[user_id].append(f"Пользователь: {user_text}")
    user_context[user_id] = user_context[user_id][-40:]

    bot.send_chat_action(message.chat.id, "typing")
    prompt = build_prompt(user_id, user_text)
    raw_answer = ask_ollama(prompt)
    clean_answer, hidden = strip_thinking_block(raw_answer)
    last_hidden_thought[user_id] = hidden
    user_context[user_id].append(f"Транзистрина: {clean_answer}")
    save_user_data(user_id)
    bot.reply_to(message, clean_answer)

if __name__ == "__main__":
    print("🤖 Транзистрина запущена. Ждёт общения...")
    bot.infinity_polling()
