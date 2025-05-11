from flask import Flask, request
import telegram
import openai
import os

# Загружаем токены
TELEGRAM_TOKEN = os.environ.get("BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Проверка токенов
if not TELEGRAM_TOKEN or not OPENAI_API_KEY:
    raise ValueError("❌ BOT_TOKEN и/или OPENAI_API_KEY не заданы в переменных окружения!")

# Инициализация
bot = telegram.Bot(token=TELEGRAM_TOKEN)
openai.api_key = OPENAI_API_KEY
app = Flask(__name__)

# Функция ИИ-гадания на 3 карты
def generate_three_card_reading(question):
    prompt = f"""
    Ты — мудрая ИИ-гадалка на картах Таро.

    Вопрос пользователя: "{question}"

    Вытяни 3 карты и опиши расклад:
    1. Карта прошлого (или причина ситуации)
    2. Карта настоящего (текущая ситуация)
    3. Карта будущего или совет

    Для каждой карты напиши:
    - Название карты с эмодзи
    - Краткое значение
    - Как карта относится к вопросу пользователя

    Напиши красиво, немного мистически, но понятно. Используй эмодзи.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,
        max_tokens=700,
        request_timeout=20  # ⏱️ Таймаут на 20 сек
    )
    return response['choices'][0]['message']['content']

# Обработка запроса от Telegram
@app.route('/webhook', methods=['POST'])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    if update.message:
        chat_id = update.message.chat.id
        text = update.message.text.strip()

        if text.lower() == "/start":
            bot.send_message(
                chat_id,
                "🔮 Привет! Я гадаю на картах Таро.\n"
                "Используй команду /ask <твой вопрос>, чтобы получить расклад."
            )

        elif text.lower() == "/about":
            bot.send_message(
                chat_id,
                "🃏 Я использую искусственный интеллект для расклада на 3 карты Таро.\n"
                "Просто задай вопрос через /ask."
            )

        elif text.lower().startswith("/ask"):
            question = text[4:].strip()
            if not question:
                bot.send_message(chat_id, "❓ Пожалуйста, задай вопрос. Пример:\n/ask Что ждёт меня в любви?")
            else:
                bot.send_message(chat_id, "🔮 Формирую расклад, подожди немного...")
                try:
                    reading = generate_three_card_reading(question)
                    bot.send_message(chat_id, reading)
                except openai.error.Timeout:
                    bot.send_message(chat_id, "⌛ Магия медлит... Попробуй ещё раз через минуту.")
                except Exception as e:
                    bot.send_message(chat_id, "⚠️ Произошёл сбой в потоке магии. Попробуй позже.")
                    print("GPT ERROR:", e)

        else:
            bot.send_message(chat_id, "❓ Неизвестная команда. Попробуй /start, /ask или /about.")

    return "OK", 200

# Домашняя страница
@app.route('/')
def home():
    return "✅ TaroXFreeBot is working."

# Установка вебхука
@app.route('/set_webhook')
def set_webhook():
    webhook_url = "https://taroxfreebot.onrender.com/webhook"
    success = bot.set_webhook(url=webhook_url)
    return f"Webhook set: {success}"
