from flask import Flask, request
import telegram
import os
import random

TOKEN = os.environ.get("BOT_TOKEN")
bot = telegram.Bot(token=TOKEN)

app = Flask(__name__)

# Примитивная база карт Таро для примера
tarot_cards = [
    "🌟 Звезда — надежда, вдохновение, внутренний свет.",
    "⚡ Башня — внезапные перемены, шок, разрушение старого.",
    "☀️ Солнце — ясность, успех, радость.",
    "🌙 Луна — иллюзии, интуиция, туманные дороги.",
    "🪄 Маг — воля, инициатива, новые возможности.",
    "🃏 Шут — начало пути, спонтанность, доверие."
]

@app.route('/webhook', methods=['POST'])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    if update.message:
        chat_id = update.message.chat.id
        text = update.message.text.lower()

        if text == "/start":
            bot.send_message(chat_id, "🔮 Добро пожаловать в TaroXFreeBot!\nЗадай вопрос или используй команду /ask для расклада.")

        elif text == "/about":
            bot.send_message(chat_id, "🤖 Этот бот гадает на Таро с помощью искусственного интеллекта.\nПросто задай вопрос или используй /ask.")

        elif text == "/ask":
            card = random.choice(tarot_cards)
            bot.send_message(chat_id, f"🃏 Я вытянул карту для тебя:\n\n{card}")

        else:
            bot.send_message(chat_id, "❓ Я не понял команду. Используй /start, /ask или /about.")

    return "OK", 200

@app.route('/')
def home():
    return "✅ TaroXFreeBot is alive."

@app.route('/set_webhook')
def set_webhook():
    webhook_url = f"https://taroxfreebot.onrender.com/webhook"
    success = bot.set_webhook(url=webhook_url)
    return f"Webhook set: {success}"
