import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Configuration - Convert admin IDs to integers
TOKEN = "7889573217:AAHjCIc2mWoEG4podoHuvoQ1qtXM1BJhWZ8"
ADMINS = [7209247941]  # Keep as is but note this is a large number
FILENAME = "usernames.txt"

# Load usernames from file
def load_usernames():
    if not os.path.exists(FILENAME):
        return []
    with open(FILENAME, "r") as f:
        return [line.strip() for line in f if line.strip()]

# Save usernames to file
def save_usernames(usernames):
    with open(FILENAME, "w") as f:
        for username in usernames:
            f.write(f"{username}\n")

# Initialize global usernames list
USERNAMES = load_usernames()

# Admin check decorator
def admin_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id not in ADMINS:
            response_text = "❌ আপনি অনুমোদিত অ্যাডমিন নন।"
            if update.message:
                await update.message.reply_text(response_text)
            elif update.callback_query:
                await update.callback_query.answer(response_text, show_alert=True)
            return
        await func(update, context)
    return wrapper

# Main menu handler
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📋 ইউজার লিস্ট", callback_data="show_list")],
        [InlineKeyboardButton("➕ ইউজার যোগ", callback_data="add_user")],
        [InlineKeyboardButton("➖ ইউজার মুছুন", callback_data="remove_user")],
        [InlineKeyboardButton("🗑️ সব মুছুন", callback_data="remove_all")],
        [InlineKeyboardButton("💬 মেসেজ", callback_data="send_message")]
    ]
    
    if update.message:
        await update.message.reply_text(
            "মেনু থেকে একটি অপশন নির্বাচন করুন:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    elif update.callback_query:
        await update.callback_query.edit_message_text(
            "মেনু থেকে একটি অপশন নির্বাচন করুন:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# Command handlers
@admin_only
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_main_menu(update, context)

@admin_only
async def add_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "❌ দয়া করে একটি ইউজারনেম লিখুন।\n\nউদাহরণ: /add babu123"
        )
        return

    username = context.args[0].lstrip("@")
    
    # Allow usernames with letters, numbers, and underscores
    if not all(c.isalnum() or c == '_' for c in username):
        await update.message.reply_text("❌ ইউজারনেম শুধুমাত্র অক্ষর, সংখ্যা এবং আন্ডারস্কোর (_) হতে হবে।")
        return

    if username in USERNAMES:
        await update.message.reply_text(f"⚠️ @{username} আগেই লিস্টে আছে।")
    else:
        USERNAMES.append(username)
        save_usernames(USERNAMES)
        await update.message.reply_text(f"✅ @{username} লিস্টে যোগ করা হয়েছে!")

@admin_only
async def remove_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "❌ দয়া করে একটি ইউজারনেম লিখুন।\n\nউদাহরণ: /remove babu123"
        )
        return

    username = context.args[0].lstrip("@")
    
    if username not in USERNAMES:
        await update.message.reply_text(f"⚠️ @{username} লিস্টে নেই।")
    else:
        USERNAMES.remove(username)
        save_usernames(USERNAMES)
        await update.message.reply_text(f"🗑️ @{username} লিস্ট থেকে মুছে ফেলা হয়েছে。")

@admin_only
async def list_usernames(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not USERNAMES:
        await update.message.reply_text("ℹ️ কোনো ইউজারনেম নেই। /add দিয়ে যোগ করুন।")
        return

    usernames_list = "\n".join([f"🔹 @{username}" for username in USERNAMES])
    await update.message.reply_text(f"📋 ইউজারনেম লিস্ট:\n\n{usernames_list}")

# Callback handler
@admin_only
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "remove_all":
        if not USERNAMES:
            await query.edit_message_text("ℹ️ কোনো ইউজারনেম নেই।")
            return
            
        # Show confirmation buttons
        keyboard = [
            [InlineKeyboardButton("✅ হ্যাঁ, সব মুছুন", callback_data="confirm_remove_all")],
            [InlineKeyboardButton("❌ না, বাতিল করুন", callback_data="menu")]
        ]
        await query.edit_message_text(
            "⚠️ আপনি কি নিশ্চিত যে আপনি সব ইউজারনেম মুছতে চান?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif query.data == "confirm_remove_all":
        USERNAMES.clear()
        save_usernames(USERNAMES)
        await query.edit_message_text("🗑️ সব ইউজারনেম মুছে ফেলা হয়েছে।")
    
    elif query.data == "show_list":
        if not USERNAMES:
            await query.edit_message_text("ℹ️ কোনো ইউজারনেম নেই।")
            return
            
        # Create a two-column layout for usernames
        keyboard = []
        for i in range(0, len(USERNAMES), 2):
            row_buttons = []
            # Add first username in this row
            if i < len(USERNAMES):
                row_buttons.append(InlineKeyboardButton(
                    f"💬 @{USERNAMES[i]}", 
                    url=f"https://t.me/{USERNAMES[i]}"
                ))
            # Add second username in this row if available
            if i+1 < len(USERNAMES):
                row_buttons.append(InlineKeyboardButton(
                    f"💬 @{USERNAMES[i+1]}", 
                    url=f"https://t.me/{USERNAMES[i+1]}"
                ))
            keyboard.append(row_buttons)
        
        # Add navigation buttons at the bottom
        keyboard.append([InlineKeyboardButton("📋 মেনু", callback_data="menu")])
        
        await query.edit_message_text(
            "📋 নিচের লিস্ট থেকে যেকোনো একজনকে চ্যাট করতে পারেন:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif query.data == "add_user":
        await query.edit_message_text(
            "ইউজারনেম যোগ করতে /add কমান্ড ব্যবহার করুন।\n\nউদাহরণ: /add username\n\n"
            "বা মেনুতে ফিরে যান:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📋 মেনু", callback_data="menu")]
            ])
        )
    
    elif query.data == "remove_user":
        await query.edit_message_text(
            "ইউজারনেম মুছতে /remove কমান্ড ব্যবহার করুন।\n\nউদাহরণ: /remove username\n\n"
            "বা মেনুতে ফিরে যান:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📋 মেনু", callback_data="menu")]
            ])
        )
    
    elif query.data == "menu":
        await show_main_menu(update, context)
    
    elif query.data == "send_message":
        if not USERNAMES:
            await query.edit_message_text("ℹ️ কোনো ইউজারনেম নেই। যোগ করুন আগে।")
            return
            
        await query.edit_message_text(
            "মেসেজ পাঠানোর জন্য নিচের ইউজার লিস্ট থেকে একজনকে সিলেক্ট করুন:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📋 ইউজার লিস্ট", callback_data="show_list")],
                [InlineKeyboardButton("📋 মেনু", callback_data="menu")]
            ])
        )

# Main application
def main():
    app = Application.builder().token(TOKEN).build()

    # Add handlers
    handlers = [
        CommandHandler("start", start),
        CommandHandler("menu", show_main_menu),
        CommandHandler("add", add_username),
        CommandHandler("remove", remove_username),
        CommandHandler("list", list_usernames),
        CallbackQueryHandler(button_handler)
    ]
    
    for handler in handlers:
        app.add_handler(handler)

    print("বট চলছে...")
    app.run_polling()

if __name__ == "__main__":
    main()
