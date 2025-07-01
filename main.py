import asyncio
from bot import start
from telegram.ext import ApplicationBuilder

async def main():
    # Инициализируем бота
    app = ApplicationBuilder().token("7964769811:AAG6Cvz9VgSms3H0KBZ2MwOTDWFiH1XkwDI").build()

    # Добавляем команды
    app.add_handler(CommandHandler("start", start))

    print("✅ Бот запущен")
    await app.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
