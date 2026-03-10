import logging
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Import your generators
from discord_gen import generate_discord_account
from roblox_gen import generate_roblox_account

# ========== CONFIG ==========
TOKEN = "YOUR_BOT_TOKEN_HERE"           # ← Replace with your bot token
# =============================

# Flask keep‑alive server
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# Start Flask in a background thread
thread = threading.Thread(target=run_flask)
thread.daemon = True
thread.start()

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== TELEGRAM HANDLERS ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎮 Generate Roblox", callback_data="gen_roblox")],
        [InlineKeyboardButton("🤖 Generate Discord", callback_data="gen_discord")],
        [InlineKeyboardButton("❓ Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🚀 **Account Generator**\n\nChoose a platform:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "gen_roblox":
        await query.edit_message_text("⏳ Generating Roblox account...")
        try:
            account = generate_roblox_account()
            if account:
                msg = (
                    f"✅ **Roblox Account Created**\n\n"
                    f"**Username:** `{account['username']}`\n"
                    f"**Password:** `{account['password']}`\n"
                    f"**Cookie:** `{account['cookie']}`"
                )
            else:
                msg = "❌ Roblox generation failed. Try again later."
        except Exception as e:
            logger.exception("Roblox error")
            msg = "❌ An error occurred."
        await query.edit_message_text(msg, parse_mode="Markdown")

    elif query.data == "gen_discord":
        await query.edit_message_text("⏳ Generating Discord account...")
        try:
            account = generate_discord_account()
            if account:
                msg = (
                    f"✅ **Discord Account Created**\n\n"
                    f"**Email:** `{account['email']}`\n"
                    f"**Password:** `{account['password']}`\n"
                    f"**Username:** `{account['username']}`\n"
                    f"**Token:** `{account['token']}`"
                )
            else:
                msg = "❌ Discord generation failed. Try again later."
        except Exception as e:
            logger.exception("Discord error")
            msg = "❌ An error occurred."
        await query.edit_message_text(msg, parse_mode="Markdown")

    elif query.data == "help":
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "❓ **How to use**\n\n"
            "Click a button to generate an account.\n"
            "The process takes about 30 seconds.\n"
            "Accounts are real and can be used immediately.",
            reply_markup=reply_markup
        )

    elif query.data == "back":
        keyboard = [
            [InlineKeyboardButton("🎮 Generate Roblox", callback_data="gen_roblox")],
            [InlineKeyboardButton("🤖 Generate Discord", callback_data="gen_discord")],
            [InlineKeyboardButton("❓ Help", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🚀 **Account Generator**\n\nChoose a platform:",
            reply_markup=reply_markup
        )

def main():
    app_bot = Application.builder().token(TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CallbackQueryHandler(button_handler))

    logger.info("Bot started.")
    app_bot.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
