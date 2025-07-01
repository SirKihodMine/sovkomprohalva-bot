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
    webhook_url = os.getenv("WEBHOOK_URL", "https://sovkomprohalva-bot.onrender.com")
    port = int(os.getenv("PORT", "8000"))

    # Создаём бота
    app = ApplicationBuilder().token("7964769811:AAG6Cvz9VgSms3H0KBZ2MwOTDWFiH1XkwDI").build()

    # Добавляем обработчики команд
    app.add_handler(CommandHandler("start", start))

    print(f"🌐 Устанавливаю webhook: {webhook_url}/webhook")

    # Устанавливаем Webhook для Telegram
    await app.bot.set_webhook(f"{webhook_url}/webhook")

    # Запускаем приложение через webhook
    await app.run_webhook(listen='0.0.0.0', port=port, url_path="")
