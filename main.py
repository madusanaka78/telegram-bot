# main.py
import telebot
import json
import os

# ---- SETTINGS ----
BOT_TOKEN = os.environ.get("BOT_TOKEN") or "PUT-YOUR-TOKEN-HERE"
OWNER_ID = 123456789   # <- Change to your numeric Telegram ID
DATA_FILE = "videos.json"
# -------------------

bot = telebot.TeleBot(BOT_TOKEN)

# load/save helpers
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(d):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

videos = load_data()  # videos mapping: { "A001": {"file_id":"...", "meta":"..."} }

# ---- Admin command: save video file_id for an ID ----
# Usage: send video file to the bot (as a private message), with caption: /save A001
@bot.message_handler(commands=['save'])
def cmd_save(message):
    # only owner can save
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "Not authorized.")
        return

    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "Use: /save <VIDEO_ID>  (attach the video with the command in the caption)")
        return
    vid = parts[1].strip()

    # check if message has video or document
    file_id = None
    if message.video:
        file_id = message.video.file_id
        ftype = "video"
    elif message.document:
        file_id = message.document.file_id
        ftype = "document"
    else:
        bot.reply_to(message, "Please attach the video (or send it as file) together with the /save <ID> caption.")
        return

    videos[vid] = {"file_id": file_id, "type": ftype}
    save_data(videos)
    bot.reply_to(message, f"Saved VIDEO ID {vid} (file_id stored).")

# ---- For convenience: a command to list saved IDs ----
@bot.message_handler(commands=['list'])
def cmd_list(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "Not authorized.")
        return
    if not videos:
        bot.reply_to(message, "No videos saved yet.")
        return
    text = "Saved videos:\n" + "\n".join(f"{k} -> {v['file_id']}" for k,v in videos.items())
    bot.reply_to(message, text)

# ---- start handler for users: send video by ID ----
@bot.message_handler(commands=['start'])
def cmd_start(message):
    parts = message.text.split()
    code = parts[1].strip() if len(parts) > 1 else ""
    if not code:
        bot.send_message(message.chat.id, "Hello — use the unlock link to open a video.")
        return

    if code not in videos:
        bot.send_message(message.chat.id, "Invalid code or video not available.")
        return

    info = videos[code]
    file_id = info["file_id"]
    # send by file_id (works fast & uses Telegram file cache)
    if info.get("type") == "video":
        bot.send_video(message.chat.id, file_id)
    else:
        # document or other: use send_document
        bot.send_document(message.chat.id, file_id)

# ---- fallback: respond politely ----
@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.reply_to(message, "Send /start <ID> from unlock link, or ask the admin to save videos with /save <ID>.")

# Run
if __name__ == "__main__":
    print("Bot started...")
    bot.infinity_polling()
