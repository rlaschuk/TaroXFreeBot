from flask import Flask, request
import telegram
import os

TOKEN = os.environ.get("BOT_TOKEN")
bot = telegram.Bot(token=TOKEN)

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    
    if update.message:
        chat_id = update.message.chat.id
        text = update.message.text
        reply = f"🔮 Ты спросил: {text}\n🃏 Ответ: карта ещё не выбрана..."
        bot.send_message(chat_id=chat_id, text=reply)
    
    return "OK", 200

@app.route('/')
def home():
    return "✅ TaroXFreeBot is alive."

@app.route('/set_webhook')
def set_webhook():
    webhook_url = f"https://taroxfreebot.onrender.com/webhook"
    success = bot.set_webhook(url=webhook_url)
    return f"Webhook set: {success}"
