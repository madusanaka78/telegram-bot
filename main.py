import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# 🔹 Render Environment Variable එකෙන් token ගන්නවා
BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = Flask(__name__)

telegram_app = Application.builder().token(BOT_TOKEN).build()

# 🔹 /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("හරි 🙂 Bot වැඩ කරනවා!")

telegram_app.add_handler(CommandHandler("start", start))

# 🔹 Telegram webhook endpoint
@app.route("/", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    telegram_app.process_update(update)
    return "ok"

# 🔹 Browser එකෙන් open කරද්දි
@app.route("/", methods=["GET"])
def home():
    return "Bot is running"

# 🔹 Render එකට PORT listen කරන කොටස (මේක අනිවාර්යයි ❗)
if __name__ == "__main__":
    telegram_app.initialize()
    telegram_app.start()
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
  )
