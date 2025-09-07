import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "8282925227:AAHu8WeujN_umN1OQoi1-D-Uv6KAQnkrF7g"
ADMINS = [7209247941]
FILENAME = "usernames.txt"

def load_usernames():
    if not os.path.exists(FILENAME):
        return []
    with open(FILENAME, "r") as f:
        return [line.strip() for line in f if line.strip()]

def save_usernames(usernames):
    with open(FILENAME, "w") as f:
        for username in usernames:
            f.write(username + "\n")

USERNAMES = load_usernames()

def is_admin(update: Update):
    return update.effective_user.id in ADMINS

def admin_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not is_admin(update):
            await update.message.reply_text("❌ আপনি অনুমোদিত অ্যাডমিন নন।")
            return
        await func(update, context)
    return wrapper

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not USERNAMES:
        await update.message.reply_text("ℹ️ এখনো কোনো ইউজারনেম নেই। /add লিখে যোগ করুন।")
        return
    keyboard = [[InlineKeyboardButton(f"💬 @{username}", url=f"https://t.me/{username}")
                 for username in USERNAMES[i:i+2]] for i in range(0, len(USERNAMES), 2)]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("📋 যেকোনো একজনকে চ্যাট করুন:", reply_markup=reply_markup)

@admin_only
async def add_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ ইউজারনেম দিন। উদাহরণ: /add babu123")
        return
    username = context.args[0].lstrip("@")
    if username in USERNAMES:
        await update.message.reply_text(f"⚠️ @{username} আগে থেকেই আছে।")
    else:
        USERNAMES.append(username)
        save_usernames(USERNAMES)
        await update.message.reply_text(f"✅ @{username} যোগ করা হয়েছে!")

@admin_only
async def remove_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ ইউজারনেম দিন। উদাহরণ: /remove babu123")
        return
    username = context.args[0].lstrip("@")
    if username not in USERNAMES:
        await update.message.reply_text(f"⚠️ @{username} নেই।")
    else:
        USERNAMES.remove(username)
        save_usernames(USERNAMES)
        await update.message.reply_text(f"🗑️ @{username} মুছে ফেলা হয়েছে।")

async def list_usernames(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not USERNAMES:
        await update.message.reply_text("ℹ️ কোনো ইউজারনেম নেই। /add দিয়ে যোগ করুন।")
        return
    text = "\n".join([f"🔹 @{username}" for username in USERNAMES])
    await update.message.reply_text(f"📋 লিস্ট:\n{text}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_username))
    app.add_handler(CommandHandler("remove", remove_username))
    app.add_handler(CommandHandler("list", list_usernames))
    print("✅ বট চলছে...")
    app.run_polling()

if __name__ == "__main__":
    main()