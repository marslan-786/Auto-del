import os
import asyncio
import re
import traceback
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)

BOT_TOKEN = "YOUR_BOT_TOKEN"

channel_timers = {}

# ⏱️ Helper: convert time string like 30s, 2m, 1h, 1d into seconds
def parse_time(time_str):
    match = re.fullmatch(r"(\d+)([smhd])", time_str.lower())
    if not match:
        return None

    value, unit = int(match.group(1)), match.group(2)
    if unit == 's':
        return value
    elif unit == 'm':
        return value * 60
    elif unit == 'h':
        return value * 60 * 60
    elif unit == 'd':
        return value * 60 * 60 * 24
    return None

# ✅ /set command
async def set_timer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if len(context.args) == 2:
            channel_username = context.args[0]
            time_str = context.args[1]

            seconds = parse_time(time_str)
            if seconds is None:
                await update.message.reply_text("⚠️ Invalid time format. Use like: 30s, 2m, 1h, 1d")
                return

            channel_timers[channel_username] = seconds
            await update.message.reply_text(f"✅ Timer for {channel_username} set to {time_str} ({seconds} seconds)")
        else:
            await update.message.reply_text("⚠️ Usage: /set <channel_username> <time>\nExample: /set @mychannel 1h")
    except Exception as e:
        await update.message.reply_text("❌ Error while setting timer")
        print("⚠️ Error in set_timer:", e)
        traceback.print_exc()

# ✅ Channel Post Handler
async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        message = update.effective_message
        chat_id = message.chat_id
        chat_username = update.effective_chat.username

        if not chat_username:
            print(f"⚠️ No username for chat_id {chat_id}, skipping")
            return

        timer = channel_timers.get(f"@{chat_username}", 60)  # default 60 sec

        await asyncio.sleep(timer)
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=message.message_id)
            print(f"🗑️ Deleted message {message.message_id} from @{chat_username} after {timer}s")
        except Exception as e:
            print(f"❌ Failed to delete message {message.message_id}: {e}")
    except Exception as e:
        print("⚠️ Error in handle_channel_post:", e)
        traceback.print_exc()

# ✅ /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text(
            "👋 I'm running!\n"
            "Use /set @channel 30s | 2m | 1h | 1d"
        )
    except Exception as e:
        print("⚠️ Error in start:", e)
        traceback.print_exc()

# 🧠 App setup
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("set", set_timer))
app.add_handler(MessageHandler(filters.ALL, handle_channel_post))

if __name__ == "__main__":
    print("🤖 Bot is running...")
    app.run_polling()