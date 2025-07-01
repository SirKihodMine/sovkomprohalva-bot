from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram import Update


# === Команда /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)
    username = user.username or "unknown"

    print(f"[INFO] Пользователь {user_id} ({username}) нажал /start")

    await update.message.reply_text("👋 Привет! Бот работает.")
