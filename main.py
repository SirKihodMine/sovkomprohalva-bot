import asyncio
from telegram.ext import CommandHandler  # ✅ Добавлено
from bot import main  # Это импортирует твою основную функцию

async def run():
    await main()

if __name__ == '__main__':
    asyncio.run(run())
