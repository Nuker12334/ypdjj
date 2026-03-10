# discord_gen_bot.py
# Telegram bot that generates Discord accounts with fill links

import requests
import random
import string
import time
import json
import os
import re
from datetime import datetime
from urllib.parse import quote

# Telegram imports
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# =============================================
# CONFIGURATION
# =============================================

TOKEN = "8555387342:AAFucFVKYfbF8Qqlj20IRhJBii5IhuxW_KE"  # Get from @BotFather
ACCOUNTS_FILE = "discord_accounts.txt"
COOLDOWN_SECONDS = 10  # Cooldown between generations

# User cooldowns
user_cooldowns = {}

# =============================================
# DISCORD ACCOUNT GENERATOR
# =============================================

def generate_username():
    """Generate Discord username"""
    patterns = [
        # 3l/4l rare style
        lambda: ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=random.randint(3, 4))),
        
        # Custom names
        lambda: random.choice(['ech0loc', 'hexsed', 'jumbajuice', 'astrow0rld', 'h3xxed', 'r1cv']),
        
        # Mixed case
        lambda: ''.join([
            random.choice(string.ascii_uppercase) if random.random() > 0.5 
            else random.choice(string.ascii_lowercase)
            for _ in range(random.randint(6, 10))
        ]),
        
        # Word + numbers
        lambda: random.choice(['cool', 'epic', 'pro', 'dark', 'shadow']) + str(random.randint(100, 999))
    ]
    
    username = random.choice(patterns)()
    
    # Add numbers sometimes
    if random.random() > 0.7:
        username += str(random.randint(1, 99))
    
    return username

def generate_email():
    """Generate temporary email"""
    domains = ['@gmail.com', '@yahoo.com', '@outlook.com', '@hotmail.com', '@protonmail.com']
    local = ''.join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(8, 12)))
    return local + random.choice(domains)

def generate_password():
    """Generate secure password"""
    length = random.randint(12, 16)
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(chars) for _ in range(length))

def generate_discord_account():
    """Generate a complete Discord account"""
    username = generate_username()
    email = generate_email()
    password = generate_password()
    
    # Format for Discord signup form
    # Discord expects: email, username, password, dob (month/day/year)
    dob_month = random.choice(['January', 'February', 'March', 'April', 'May', 'June', 
                               'July', 'August', 'September', 'October', 'November', 'December'])
    dob_day = str(random.randint(1, 28))
    dob_year = str(random.randint(1980, 2005))
    
    return {
        'username': username,
        'email': email,
        'password': password,
        'dob_month': dob_month,
        'dob_day': dob_day,
        'dob_year': dob_year,
        'created_at': datetime.now().isoformat()
    }

def create_fill_link(account):
    """Create a URL with pre-filled Discord signup info"""
    # Base Discord register URL
    base = "https://discord.com/register"
    
    # Create query parameters
    params = {
        'email': account['email'],
        'username': account['username'],
        'global_name': account['username'],  # Display name same as username
        'password': account['password'],
        'birth_month': account['dob_month'],
        'birth_day': account['dob_day'],
        'birth_year': account['dob_year']
    }
    
    # Build URL with encoded parameters
    query = '&'.join([f"{k}={quote(v)}" for k, v in params.items()])
    url = f"{base}?{query}"
    
    return url

def save_account(account):
    """Save account to file"""
    with open(ACCOUNTS_FILE, 'a') as f:
        f.write(f"Username: {account['username']}\n")
        f.write(f"Email: {account['email']}\n")
        f.write(f"Password: {account['password']}\n")
        f.write(f"Created: {account['created_at']}\n")
        f.write("-" * 40 + "\n")

def load_accounts():
    """Load all saved accounts"""
    if not os.path.exists(ACCOUNTS_FILE):
        return []
    
    with open(ACCOUNTS_FILE, 'r') as f:
        content = f.read()
    
    # Simple parsing - split by separator
    accounts_raw = content.split("-" * 40)
    accounts = []
    
    for acc_raw in accounts_raw:
        if not acc_raw.strip():
            continue
        
        acc = {}
        for line in acc_raw.strip().split('\n'):
            if ': ' in line:
                key, value = line.split(': ', 1)
                if key == 'Username':
                    acc['username'] = value
                elif key == 'Email':
                    acc['email'] = value
                elif key == 'Password':
                    acc['password'] = value
        if acc:
            accounts.append(acc)
    
    return accounts

# =============================================
# CHECK COOLDOWN
# =============================================

def check_cooldown(user_id):
    """Check if user is on cooldown"""
    if user_id in user_cooldowns:
        last_time = user_cooldowns[user_id]
        elapsed = time.time() - last_time
        if elapsed < COOLDOWN_SECONDS:
            return COOLDOWN_SECONDS - elapsed
    return 0

def update_cooldown(user_id):
    """Update user's last generation time"""
    user_cooldowns[user_id] = time.time()

# =============================================
# TELEGRAM HANDLERS
# =============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome message with buttons"""
    keyboard = [
        [InlineKeyboardButton("🚀 Generate Discord Account", callback_data='gen')],
        [InlineKeyboardButton("📋 View My Accounts", callback_data='view')],
        [InlineKeyboardButton("❓ Help", callback_data='help')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🤖 *Discord Account Generator Bot*\n\n"
        "Generate Discord accounts with pre-filled links!\n"
        f"⏱️ Cooldown: {COOLDOWN_SECONDS} seconds\n\n"
        "Click a button below to start:",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if query.data == 'gen':
        # Check cooldown
        cooldown = check_cooldown(user_id)
        if cooldown > 0:
            await query.edit_message_text(
                f"⏳ Please wait {cooldown:.1f} seconds before generating again."
            )
            return
        
        # Generate account
        await query.edit_message_text("⚙️ Generating Discord account...")
        
        account = generate_discord_account()
        fill_url = create_fill_link(account)
        
        # Save to file
        save_account(account)
        update_cooldown(user_id)
        
        # Create buttons for the generated account
        keyboard = [
            [InlineKeyboardButton("🔗 Open Pre-filled Form", url=fill_url)],
            [InlineKeyboardButton("📋 Copy Combo", callback_data=f'copy_{account["email"]}:{account["password"]}')],
            [InlineKeyboardButton("🔄 Generate Another", callback_data='gen')],
            [InlineKeyboardButton("🏠 Main Menu", callback_data='menu')]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"✅ *Account Generated!*\n\n"
            f"**Username:** `{account['username']}`\n"
            f"**Email:** `{account['email']}`\n"
            f"**Password:** `{account['password']}`\n\n"
            f"**Birthday:** {account['dob_month']} {account['dob_day']}, {account['dob_year']}\n\n"
            f"Click the button below to open pre-filled Discord signup form.\n"
            f"Just solve the captcha and click Create!",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    elif query.data.startswith('copy_'):
        # Copy combo (email:password)
        combo = query.data.replace('copy_', '')
        await query.edit_message_text(
            f"📋 *Copy this combo:*\n\n`{combo}`\n\nYou can now paste it anywhere.",
            parse_mode='Markdown'
        )
        
        # Add back button after 3 seconds
        await asyncio.sleep(3)
        
        keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data='menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "Return to main menu?",
            reply_markup=reply_markup
        )
    
    elif query.data == 'view':
        # Show user's generated accounts
        accounts = load_accounts()
        
        if not accounts:
            await query.edit_message_text(
                "📭 No accounts generated yet.\n\nUse /gen to create your first account!"
            )
            return
        
        # Show last 5 accounts
        recent = accounts[-5:] if len(accounts) > 5 else accounts
        
        message = "📋 *Your Recent Accounts:*\n\n"
        for i, acc in enumerate(reversed(recent), 1):
            message += f"{i}. `{acc['email']}:{acc['password']}`\n"
        
        keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data='menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    elif query.data == 'help':
        keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data='menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "❓ *How to use:*\n\n"
            "1. Click 'Generate Discord Account'\n"
            "2. Click the link to open pre-filled Discord signup\n"
            "3. Solve the captcha and click Create\n"
            "4. Your account is ready!\n\n"
            f"⏱️ Cooldown: {COOLDOWN_SECONDS} seconds between generations\n"
            "💾 Accounts are automatically saved to file\n"
            "📋 Use 'Copy Combo' to get email:password format",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    elif query.data == 'menu':
        # Return to main menu
        keyboard = [
            [InlineKeyboardButton("🚀 Generate Discord Account", callback_data='gen')],
            [InlineKeyboardButton("📋 View My Accounts", callback_data='view')],
            [InlineKeyboardButton("❓ Help", callback_data='help')]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🤖 *Discord Account Generator Bot*\n\n"
            f"⏱️ Cooldown: {COOLDOWN_SECONDS} seconds\n\n"
            "Choose an option:",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

async def gen_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Direct /gen command"""
    # Trigger the same as button
    await button_handler(update, context)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show bot statistics"""
    accounts = load_accounts()
    await update.message.reply_text(
        f"📊 *Bot Statistics*\n\n"
        f"Total accounts generated: {len(accounts)}\n"
        f"Cooldown: {COOLDOWN_SECONDS}s\n"
        f"File: {ACCOUNTS_FILE}",
        parse_mode='Markdown'
    )

# =============================================
# MAIN BOT SETUP
# =============================================

def main():
    """Start the bot"""
    # Create application
    app = Application.builder().token(TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gen", gen_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("🤖 Discord Account Generator Bot is running!")
    print(f"📁 Accounts will be saved to: {ACCOUNTS_FILE}")
    print("Press Ctrl+C to stop")
    
    # Start bot
    app.run_polling()

# =============================================
# RUN
# =============================================

if __name__ == "__main__":
    main()
