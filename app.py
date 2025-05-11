from flask import Flask, request
import telegram
import os
from openai import OpenAI
from openai import OpenAIError, APITimeoutError

# Загружаем токены
TELEGRAM_TOKEN = os.environ.get("BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Проверка токенов
if not TELEGRAM_TOKEN or not OPENAI_API_KEY:
    raise ValueError("❌ BOT_TOKEN и/или OPENAI_API_KEY не заданы в переменных окружения!")

# Инициализация клиентов
bot = telegram.Bot(token=TELEGRAM_TOKEN)
openai_client = OpenAI(api_key=OPENAI_API_KEY)
app = Flask(__name__)

# Функция ИИ-гадания на 3 карты
def generate_three_card_reading(question):
    prompt = f"""
    Ты — мудрая и немного загадочная гадалка, умеющая читать карты Таро с теплом, лёгкой иронией и настоящим вниманием к человеку.

    Сейчас к тебе обратился человек с вопросом: "{question}"

    Вытяни три карты Таро — первую, вторую и третью.

    Для каждой:
    — Назови карту 🎴
    — Расскажи, что она означает именно в контексте этого вопроса
    — Поясни с примерами из жизни, ассоциациями или эмоциями
    — Говори живо, по-дружески, избегай сухих формулировок
    — Не используй банальных фраз вроде "всё в твоих руках", лучше дай тёплое напутствие или легкий совет

    В конце — короткий вывод: что подсказывает расклад в целом. Поддержи человека, чтобы он почувствовал уверенность.

    Не забывай: ты не просто ИИ, а проводник между картами и душой. ✨
    Используй эмодзи, когда уместно, но не переборщи.

    Делай короткие описания !!!
    """

    # prompt = f"""
    # Ты — мудрая ИИ-гадалка на картах Таро.

    # Вопрос пользователя: "{question}"

    # Вытяни 3 карты и опиши расклад

    # Напиши красиво. Используй эмодзи.
    # """

    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,
        max_tokens=700,
        timeout=20  # тайм-аут в секундах
    )
    return response.choices[0].message.content

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
            try:
                question = text[4:].strip()
                if not question:
                    bot.send_message(
                        chat_id,
                        "❓ Пожалуйста, задай вопрос. Пример:\n/ask Что ждёт меня в любви?"
                    )
                else:
                    bot.send_message(chat_id, "🔮 Формирую расклад, подожди немного...")
                    reading = generate_three_card_reading(question)
                    bot.send_message(chat_id, reading)
            except APITimeoutError:
                bot.send_message(chat_id, "⌛ Магия медлит... Попробуй ещё раз через минуту.")
            except OpenAIError as e:
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
