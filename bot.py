import os
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram import Update


# === Команда /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привет! Бот работает.")


# === Функция main(), которую можно импортировать ===
async def main():
    """
    Создаёт и запускает бота через webhook
    """

    # Получаем URL и порт из переменных окружения
    webhook_url = os.getenv("WEBHOOK_URL", "https://sovkomprohalva-bot.onrender.com ")
    port = int(os.getenv("PORT", "8000"))

    # Создаём бота
    app = ApplicationBuilder().token("ТОКЕН_БОТА").build()

    # Добавляем команды
    app.add_handler(CommandHandler("start", start))

    # Устанавливаем webhook
    await app.bot.set_webhook(f"{webhook_url}/webhook")

    # Запускаем webhook
    await app.run_webhook(listen='0.0.0.0', port=port, url_path="")
