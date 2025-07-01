from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram import Update


# === Команда /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привет! Бот работает.")


# === Функция main(), которую можно импортировать ===
async def main():
    """
    Создаёт и запускает бота
    """
    app = ApplicationBuilder().token("ТОКЕН_БОТА").build()
    app.add_handler(CommandHandler("start", start))
    print("✅ Бот запущен через webhook")
    await app.run_polling()
